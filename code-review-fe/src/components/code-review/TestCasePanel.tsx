/* eslint-disable */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useCodeStore } from "@/store/codeStore";
import { Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Skeleton } from "../ui/skeleton";

export default function TestCasePanel() {
  const { code } = useCodeStore() as any;
  const [results, setResults] = useState<any[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string | undefined>(undefined);

  const handleRun = async () => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await fetch("http://localhost:8080/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          assignment: { content: "This is test version", language: "cpp" },
          submission: { code },
          testcase: [
            {
              name: "Testcase 01",
              input: "   Hello   world   ",
              expect: "Hello world",
            },
            {
              name: "Testcase 02",
              input: "  OpenAI    GPT    5  ",
              expect: "OpenAI GPT 5",
            },
            {
              name: "Testcase 03",
              input: "NoExtraSpace",
              expect: "NoExtraSpace",
            },
          ],
        }),
      });

      const data = await res.json();
      console.log('========',data)

      const compileError = data.errorMessage || "";

      if (compileError) {
        setError(compileError);
        setResults(null);
        setActiveTab(undefined);
        return;
      }

      const testcaseResults = data.testcaseResults ?? [];

      setResults(testcaseResults);
      setError(null);
      if (testcaseResults.length > 0) {
        setActiveTab(testcaseResults[0].name);
      } else {
        setActiveTab(undefined);
      }
    } catch (err) {
      console.error(err);
      setError("Có lỗi xảy ra khi chạy test. Vui lòng thử lại.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-3 border rounded-md flex flex-col h-full">
      <h2 className="font-semibold mb-2">Test Case</h2>

      <Button onClick={handleRun} disabled={isLoading}>
        {isLoading ? <Loader2 className="animate-spin" /> : "Run"}
      </Button>

      <div className="flex-1 min-h-0 mt-3">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
            <div className="font-semibold mb-1">Compile / Syntax Error</div>
            <pre className="text-xs whitespace-pre-wrap">{error}</pre>
          </div>
        )}

        {isLoading ? (
          <div className="pt-2 space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-5 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        ) : (
          !error &&
          results &&
          results.length > 0 && (
            <Tabs
              value={activeTab}
              onValueChange={setActiveTab}
              className="h-full flex flex-col"
            >
              <TabsList className="w-full overflow-x-auto">
                {results.map((tc) => (
                  <TabsTrigger
                    key={tc.name}
                    value={tc.name}
                    className="text-xs sm:text-sm flex items-center gap-1"
                  >
                    {tc.name}
                  </TabsTrigger>
                ))}
              </TabsList>

              <div className="flex-1 min-h-0 mt-3">
                <ScrollArea className="h-full">
                  {results.map((tc) => (
                    <TabsContent
                      key={tc.name}
                      value={tc.name}
                      className="mt-0 space-y-2 text-sm"
                    >
                      <div>
                        <span className="font-semibold">Status: </span>
                        <span
                          className={
                            tc.status === "PASSED"
                              ? "text-green-600"
                              : "text-red-600"
                          }
                        >
                          {tc.status}
                        </span>
                      </div>

                      <div>
                        <div className="font-semibold text-xs uppercase text-gray-500">
                          Input
                        </div>
                        <pre className="text-xs bg-muted rounded-md p-2 whitespace-pre-wrap">
                          {tc.input}
                        </pre>
                      </div>

                      <div>
                        <div className="font-semibold text-xs uppercase text-gray-500">
                          Expect
                        </div>
                        <pre className="text-xs bg-muted rounded-md p-2 whitespace-pre-wrap">
                          {tc.expect}
                        </pre>
                      </div>

                      <div>
                        <div className="font-semibold text-xs uppercase text-gray-500">
                          Actual
                        </div>
                        <pre className="text-xs bg-muted rounded-md p-2 whitespace-pre-wrap">
                          {tc.actual}
                        </pre>
                      </div>
                      {tc.errorMessage && tc.errorMessage.trim() !== "" && (
                        <div>
                          <div className="font-semibold text-xs uppercase text-red-500">
                            Error
                          </div>
                          <pre className="text-xs bg-red-50 border border-red-200 rounded-md p-2 whitespace-pre-wrap text-red-700">
                            {tc.errorMessage}
                          </pre>
                        </div>
                      )}
                    </TabsContent>
                  ))}
                </ScrollArea>
              </div>
            </Tabs>
          )
        )}

        {!error && (!results || results.length === 0) && !isLoading && (
          <p className="text-xs text-gray-500">
            Nhấn <span className="font-semibold">Run</span> để chạy test case.
          </p>
        )}
      </div>
    </div>
  );
}
