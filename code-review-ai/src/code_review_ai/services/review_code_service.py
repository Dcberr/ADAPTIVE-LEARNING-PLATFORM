import logging
import inspect
from time import perf_counter
from code_review_ai.agents.fix_hint_agent import FixHintAgent
from code_review_ai.agents.improvement_agent import ImprovementAgent
from code_review_ai.agents.logic_agent import LogicAgent
from code_review_ai.agents.overview_agent import OverviewAgent
from code_review_ai.agents.review_link_agent import ReviewLinkAgent
from code_review_ai.models.review_state import ReviewState
from code_review_ai.utils.debug_logging import snapshot_review_state, summarize_state
from langgraph.graph import StateGraph
from typing import cast


logger = logging.getLogger(__name__)


class ReviewCodeService:
    def __init__(
        self,
        logic_agent: LogicAgent,
        fix_hint_agent: FixHintAgent,
        improvement_agent: ImprovementAgent,
        review_link_agent: ReviewLinkAgent,
        overview_agent: OverviewAgent,
    ):
        self.logic_agent = logic_agent
        self.fix_hint_agent = fix_hint_agent
        self.improvement_agent = improvement_agent
        self.review_link_agent = review_link_agent
        self.overview_agent = overview_agent

        # Build the workflow graph
        self.workflow = self.create_review_graph()

    def create_review_graph(self):
        workflow = StateGraph(ReviewState)

        # Add nodes for each agent
        workflow.add_node(
            "logic", self._instrument_node("logic", self.logic_agent.analyze)
        )
        workflow.add_node(
            "fix_hint",
            self._instrument_node("fix_hint", self.fix_hint_agent.analyze),
        )
        workflow.add_node(
            "improve",
            self._instrument_node("improve", self.improvement_agent.analyze),
        )
        workflow.add_node(
            "review_link",
            self._instrument_node("review_link", self.review_link_agent.analyze),
        )
        workflow.add_node(
            "overview",
            self._instrument_node("overview", self.overview_agent.analyze),
        )

        workflow.set_entry_point("logic")

        # Conditional routing functions
        def route_after_logic(state: ReviewState) -> str:
            logger.debug(
                "Determining route after logic with summary: %s",
                summarize_state(state),
            )
            if state["logic_issues"] and len(state["logic_issues"]) > 0:
                logger.debug("Route selected: logic -> fix_hint")
                return "fix_hint"
            if state.get("needs_improvement"):
                logger.debug("Route selected: logic -> improve (needs_improvement)")
                return "improve"
            logger.debug("Route selected: logic -> improve")
            return "improve"

        # Add conditional edges
        workflow.add_conditional_edges(
            "logic",
            route_after_logic,
            {
                "fix_hint": "fix_hint",
                "improve": "improve",
            },
        )
        workflow.add_conditional_edges(
            "fix_hint",
            lambda s: "review_link",
            {"review_link": "review_link"},
        )
        workflow.add_conditional_edges(
            "review_link",
            lambda s: "improve",
            {"improve": "improve"},
        )
        workflow.add_conditional_edges(
            "improve",
            lambda s: "overview",
            {"overview": "overview"},
        )

        workflow.set_finish_point("overview")

        return workflow.compile()

    def _instrument_node(self, node_name: str, handler):
        if inspect.iscoroutinefunction(handler):
            async def wrapped(state: ReviewState):
                start = perf_counter()
                logger.debug(
                    "Entering node '%s' with state summary: %s",
                    node_name,
                    summarize_state(state),
                )
                result = await handler(state)
                elapsed_ms = (perf_counter() - start) * 1000
                logger.debug(
                    "Leaving node '%s' after %.2f ms with state summary: %s",
                    node_name,
                    elapsed_ms,
                    summarize_state(result),
                )
                logger.debug(
                    "State snapshot after node '%s': %s",
                    node_name,
                    snapshot_review_state(result),
                )
                return result

            return wrapped

        def wrapped(state: ReviewState):
            start = perf_counter()
            logger.debug(
                "Entering node '%s' with state summary: %s",
                node_name,
                summarize_state(state),
            )
            result = handler(state)
            elapsed_ms = (perf_counter() - start) * 1000
            logger.debug(
                "Leaving node '%s' after %.2f ms with state summary: %s",
                node_name,
                elapsed_ms,
                summarize_state(result),
            )
            logger.debug(
                "State snapshot after node '%s': %s",
                node_name,
                snapshot_review_state(result),
            )
            return result

        return wrapped

    async def review_code(self, state: ReviewState) -> ReviewState:
        """Run the full review workflow on a student's submission state using TypedDict."""

        logger.debug(
            "Starting review workflow with state summary: %s", summarize_state(state)
        )

        # Run the workflow
        final_state_dict = await self.workflow.ainvoke(state)

        logger.debug(
            "Review workflow finished with state summary: %s",
            summarize_state(final_state_dict),
        )

        # Cast the returned dict to ReviewState TypedDict
        return cast(ReviewState, final_state_dict)
