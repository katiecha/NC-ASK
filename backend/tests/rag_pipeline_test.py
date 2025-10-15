import asyncio
from services.service_factory import ServiceFactory

async def main():
    factory = ServiceFactory()
    pipeline = factory.create_rag_pipeline()

    result = await pipeline.process_query("What resources are available for autism support?")

    print("\nAnswer:", result["response"])
    print("Citations:", result["citations"])
    print("Crisis detected?", result["crisis_detected"])

if __name__ == "__main__":
    asyncio.run(main())
