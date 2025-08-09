import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/customers/?page=1&page_size=20")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total items: {data.get('total', 0)}")
            print(f"Total pages: {data.get('total_pages', 0)}")
            print(f"Items count: {len(data.get('items', []))}")
            if data.get('items'):
                print(f"First item: {data['items'][0]}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api())