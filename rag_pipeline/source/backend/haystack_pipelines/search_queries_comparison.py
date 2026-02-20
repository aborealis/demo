from haystack_pipelines.helpers.common import pipeline_constructor
from haystack_pipelines.helpers.templates import SEARCH_QUERIES_COMPARISON_TEMPLATE


def search_queries_comparison_pipeline():
    return pipeline_constructor(
        template=SEARCH_QUERIES_COMPARISON_TEMPLATE,
        required_variables=["search_query", "search_queries"],
        generation_kwargs={}
    )


if __name__ == "__main__":
    queries = ["login error", "password reset"]

    SEARCH_QUERIES_COMPARISON_PIPELINE = search_queries_comparison_pipeline()
    result = SEARCH_QUERIES_COMPARISON_PIPELINE.run({
        "prompt": {
            "search_queries": queries,
            "search_query": "login issue with VPN enabled"
        }
    })["llm"]["replies"][0]

    print(result)
