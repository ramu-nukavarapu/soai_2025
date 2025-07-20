import requests
import asyncio
import aiohttp
import streamlit as st

# Fetch data from NocoDB
@st.cache_data(show_spinner=False)
def fetch_registrations_data(aidev_url, techlead_url, headers):
    aidev = fetch_registrations(aidev_url, headers)
    techlead = fetch_registrations(techlead_url, headers)
    return aidev, techlead

@st.cache_data(show_spinner=False)
def fetch_registrations(url, headers):
    try:
        offset = 0
        total_data = []

        while True:
            response = requests.get(
                url,
                headers=headers,
                params={
                    "limit": 1000,
                    "offset": offset,
                    "fields": "Full Name,Affiliation (College/Company/Organization Name),Id,Age,Gender,Email Address,Contact Number"
                }
            )
            response.raise_for_status()
            data = response.json().get("list", [])
            total_data.extend(data)
            offset += 1000
            if len(data) < 1000:
                break

        return total_data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

async def fetch_page(session, page, GITLAB_URL, HEADERS):
    url = f"{GITLAB_URL}/api/v4/users"
    async with session.get(url, headers=HEADERS, params={"per_page": 100, "page": page}) as response:
        try:
            return await response.json()
        except Exception as e:
            text = await response.text()
            raise RuntimeError(f"Failed to decode JSON on page {page}: {e} — Response: {text}")

async def fetch_gitlab_users_concurrent(total_pages, GITLAB_URL, HEADERS):
    users = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_page(session, page, GITLAB_URL, HEADERS) for page in range(0, total_pages + 1)]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                users.extend(result)

    return users

# To run the async function
@st.cache_data(show_spinner=False)
def fetch_gitlab_users(GITLAB_URL, HEADERS):
    return asyncio.run(fetch_gitlab_users_concurrent(501, GITLAB_URL, HEADERS))

@st.cache_data(show_spinner=False)
def fetch_corpus_data(url, headers):
    users = []
    skip = 0
    while True:
        response = requests.get(url, headers=headers, params={
            'skip': skip,
            'limit': 1000
        })
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break
        data = response.json()
        users.extend(data)
        skip += 1000
        if not data:
            break

    return users

@st.cache_data(show_spinner=False)
def fetch_corpus_records_data(url, headers):
    all_records = []
    skip = 0
    limit = 1000  # Keep reasonable batch size
    page = 1
    
    try:
        while True:
            url = f"https://backend2.swecha.org/api/v1/records/?skip={skip}&limit={limit}"

            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                break
            
            # If no data returned, we've reached the end
            if not data:
                break
            
            # Add records to our collection
            all_records.extend(data)
            
            # If we got less than the limit, we've reached the end
            if len(data) < limit:
                break
            
            # Prepare for next iteration
            skip += limit
            page += 1
            
        return all_records
        
    except Exception as e:
        return []