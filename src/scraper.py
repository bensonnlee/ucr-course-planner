"""
This module contains the code to fetch course data from the UCR registration system.
"""
import requests


def fetch_course_data(term: str = "202440") -> list[dict]:
    """
    Fetch course data from the UCR registration system.
    
    Args:
        term: Term code (e.g., "202440" for Fall 2024)
              Format: YYYY + QQ where QQ is 10=winter, 20=spring, 30=summer, 40=fall
    
    Returns:
        list[dict]: A list of dictionaries, each containing course data.
    """
    
    # get session cookies
    session = requests.Session()
    session.get("https://registrationssb.ucr.edu")
    
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    
    # initialize search session
    session.post(
        "https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search",
        data={"term": term},
        headers=headers,
    )
    
    # get total count first
    url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_term={term}&pageOffset=0&pageMaxSize=1&sortColumn=subjectDescription&sortDirection=asc"
    response = session.get(url, headers=headers)
    response.raise_for_status()
    
    total_count = response.json()["totalCount"]
    print(f"Total courses available: {total_count}")
    
    # fetch all courses with pagination
    courses = []
    page_offset = 0
    page_size = 500  # reasonable batch size
    
    while page_offset < total_count:
        print(f"Fetching courses {page_offset} to {min(page_offset + page_size, total_count)}...")
        
        url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_term={term}&pageOffset={page_offset}&pageMaxSize={page_size}&sortColumn=subjectDescription&sortDirection=asc"
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        batch_data = response.json()["data"]
        if not batch_data:
            print("No more data returned, stopping...")
            break
            
        courses.extend(batch_data)
        page_offset += len(batch_data)
        
        # break if we got less than expected (last page)
        if len(batch_data) < page_size:
            break
    
    print(f"Successfully fetched {len(courses)} courses")
    
    return courses


if __name__ == "__main__":
    fetch_course_data()