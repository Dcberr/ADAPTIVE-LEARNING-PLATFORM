import os
from fastapi import Depends, Request
from openai import OpenAI
from app.agents.logic_agent import LogicAgent
from app.agents.concept_mapping_agent import ConceptMappingAgent
from app.agents.fix_hint_agent import FixHintAgent
from app.agents.generate_testcase_agent import GenerateTestcaseAgent
from app.agents.improvement_agent import ImprovementAgent
from app.agents.overview_agent import OverviewAgent
from app.agents.reflection_agent import ReflectionAgent
from app.services.review_code_service import ReviewCodeService
from app.tools.execution_run_tool import ExecutionRunTool


DEFAULT_FIREWORKS_MODEL = "accounts/fireworks/models/qwen3-coder-480b-a35b-instruct"


def get_fireworks_client(request: Request) -> OpenAI:
    client = getattr(request.app.state, "fireworks_client", None)
    if client is None:
        raise RuntimeError("Fireworks client is not initialized on application startup.")
    return client


def get_fireworks_model_name() -> str:
    return os.environ.get("FIREWORKS_MODEL", DEFAULT_FIREWORKS_MODEL)


def get_logic_agent(client=Depends(get_fireworks_client)) -> LogicAgent:
    return LogicAgent(
        client=client,
        model_name=get_fireworks_model_name(),
    )


def get_concept_mapping_agent(
    client=Depends(get_fireworks_client),
) -> ConceptMappingAgent:
    return ConceptMappingAgent(client=client, model_name=get_fireworks_model_name())


def get_fix_hint_agent(client=Depends(get_fireworks_client)) -> FixHintAgent:
    return FixHintAgent(client=client, model_name=get_fireworks_model_name())


def get_execution_run_tool() -> ExecutionRunTool:
    return ExecutionRunTool.from_env()


def get_generate_testcase_agent(
    client=Depends(get_fireworks_client),
    execution_tool: ExecutionRunTool = Depends(get_execution_run_tool),
) -> GenerateTestcaseAgent:
    return GenerateTestcaseAgent(
        client=client,
        model_name=get_fireworks_model_name(),
        execution_tool=execution_tool,
    )


def get_improvement_agent(client=Depends(get_fireworks_client)) -> ImprovementAgent:
    return ImprovementAgent(client=client, model_name=get_fireworks_model_name())


def get_overview_agent(client=Depends(get_fireworks_client)) -> OverviewAgent:
    return OverviewAgent(client=client, model_name=get_fireworks_model_name())


def get_reflection_agent(client=Depends(get_fireworks_client)) -> ReflectionAgent:
    return ReflectionAgent(client=client, model_name=get_fireworks_model_name())


# -----------------------------
# Dependency for ReviewCodeService
# -----------------------------
def get_review_service(
    logic_agent: LogicAgent = Depends(get_logic_agent),
    concept_mapping_agent: ConceptMappingAgent = Depends(get_concept_mapping_agent),
    fix_hint_agent: FixHintAgent = Depends(get_fix_hint_agent),
    generate_testcase_agent: GenerateTestcaseAgent = Depends(get_generate_testcase_agent),
    improvement_agent: ImprovementAgent = Depends(get_improvement_agent),
    overview_agent: OverviewAgent = Depends(get_overview_agent),
    reflection_agent: ReflectionAgent = Depends(get_reflection_agent),
) -> ReviewCodeService:
    return ReviewCodeService(
        logic_agent=logic_agent,
        concept_mapping_agent=concept_mapping_agent,
        fix_hint_agent=fix_hint_agent,
        generate_testcase_agent=generate_testcase_agent,
        improvement_agent=improvement_agent,
        overview_agent=overview_agent,
        reflection_agent=reflection_agent,
    )
