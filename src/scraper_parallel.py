"""
This module contains the parallelized code to fetch course data from the UCR registration system.
"""
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time
from typing import List, Dict, Tuple


class UCRCourseFetcher:
    def __init__(self, max_workers: int = 20):
        """
        Initialize the course fetcher with configurable concurrency.
        
        Args:
            max_workers: Maximum number of concurrent threads for prerequisite fetching
        """
        self.max_workers = max_workers
        self.session_lock = Lock()
        
    def create_session(self) -> requests.Session:
        """Create a new session with UCR authentication cookies."""
        session = requests.Session()
        session.get("https://registrationssb.ucr.edu")
        return session

    def fetch_prerequisite_worker(self, args: Tuple[str, str, str]) -> Tuple[str, str]:
        """
        Worker function to fetch prerequisite for a single course.
        
        Args:
            args: Tuple of (term, course_reference_number, session_cookies)
        
        Returns:
            Tuple of (course_reference_number, prerequisite_text)
        """
        term, course_reference_number, session_cookies = args
        
        # Create a new session for this thread
        session = requests.Session()
        session.cookies.update(session_cookies)
        
        try:
            url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites?term={term}&courseReferenceNumber={course_reference_number}"
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if no prerequisites
            if "No prerequisite information available" in response.text:
                return course_reference_number, ""
            
            # Extract prerequisite text from the structured HTML
            prereq_section = soup.find('section', {'aria-labelledby': 'preReqs'})
            if not prereq_section:
                return course_reference_number, ""
            
            # Get all <pre> tags which contain the prerequisite text
            pre_tags = prereq_section.find_all('pre')
            if not pre_tags:
                return course_reference_number, ""
            
            # Combine all prerequisite text
            prerequisite_text = ''.join(tag.get_text().strip() for tag in pre_tags)
            return course_reference_number, prerequisite_text.strip() if prerequisite_text else ""
            
        except Exception as e:
            print(f"Error fetching prerequisites for CRN {course_reference_number}: {e}")
            return course_reference_number, ""

    def fetch_prerequisites_parallel(self, courses: List[Dict], term: str, session: requests.Session) -> Dict[str, str]:
        """
        Fetch prerequisites for all courses in parallel.
        
        Args:
            courses: List of course dictionaries
            term: Term code
            session: Authenticated session
        
        Returns:
            Dictionary mapping course_reference_number to prerequisite text
        """
        print(f"Fetching prerequisites for {len(courses)} courses using {self.max_workers} workers...")
        
        # Prepare arguments for worker threads
        worker_args = []
        for course in courses:
            crn = course.get("courseReferenceNumber")
            if crn:
                worker_args.append((term, crn, session.cookies))
        
        # Track results
        prerequisites = {}
        completed_count = 0
        start_time = time.time()
        
        # Execute prerequisite fetching in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_crn = {
                executor.submit(self.fetch_prerequisite_worker, args): args[1] 
                for args in worker_args
            }
            
            # Process completed tasks
            for future in as_completed(future_to_crn):
                crn, prerequisite_text = future.result()
                prerequisites[crn] = prerequisite_text
                completed_count += 1
                
                # Progress update every 50 completions
                if completed_count % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed
                    remaining = len(worker_args) - completed_count
                    eta = remaining / rate if rate > 0 else 0
                    print(f"Prerequisites: {completed_count}/{len(worker_args)} complete "
                          f"({rate:.1f}/sec, ETA: {eta:.1f}s)")
        
        elapsed = time.time() - start_time
        print(f"Completed prerequisite fetching in {elapsed:.1f}s ({len(worker_args)/elapsed:.1f} requests/sec)")
        
        return prerequisites

    def fetch_course_batch(self, session: requests.Session, term: str, page_offset: int, page_size: int) -> List[Dict]:
        """
        Fetch a single batch of courses.
        
        Args:
            session: Authenticated session
            term: Term code
            page_offset: Starting offset for pagination
            page_size: Number of courses to fetch
        
        Returns:
            List of course dictionaries
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_term={term}&pageOffset={page_offset}&pageMaxSize={page_size}&sortColumn=subjectDescription&sortDirection=asc"
        
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()["data"]

    def fetch_course_data_parallel(self, term: str = "202440", include_prerequisites: bool = True, 
                                 batch_size: int = 500, course_batch_workers: int = 20) -> List[Dict]:
        """
        Fetch course data from the UCR registration system with parallelization.
        
        Args:
            term: Term code (e.g., "202440" for Fall 2024)
            include_prerequisites: Whether to fetch prerequisite information for each course
            batch_size: Number of courses to fetch per batch
            course_batch_workers: Number of concurrent workers for course batch fetching
        
        Returns:
            List of dictionaries, each containing course data.
        """
        start_time = time.time()
        
        # Create main session and initialize search
        session = self.create_session()
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
        
        # Initialize search session
        session.post(
            "https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search",
            data={"term": term},
            headers=headers,
        )
        
        # Get total count first
        url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_term={term}&pageOffset=0&pageMaxSize=1&sortColumn=subjectDescription&sortDirection=asc"
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        total_count = response.json()["totalCount"]
        print(f"Total courses available: {total_count}")
        
        # Prepare batch arguments for parallel fetching
        batch_args = []
        page_offset = 0
        while page_offset < total_count:
            current_batch_size = min(batch_size, total_count - page_offset)
            batch_args.append((term, page_offset, current_batch_size))
            page_offset += current_batch_size
        
        print(f"Fetching courses in {len(batch_args)} batches using {course_batch_workers} workers...")
        
        # Fetch course batches in parallel (with limited concurrency to avoid overwhelming server)
        courses = []
        completed_batches = 0
        
        with ThreadPoolExecutor(max_workers=course_batch_workers) as executor:
            # Create sessions for each worker
            sessions = [self.create_session() for _ in range(course_batch_workers)]
            session_iter = iter(sessions * (len(batch_args) // len(sessions) + 1))
            
            # Initialize each session
            for worker_session in sessions:
                worker_session.post(
                    "https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search",
                    data={"term": term},
                    headers=headers,
                )
            
            # Submit batch fetch tasks
            future_to_batch = {
                executor.submit(self.fetch_course_batch, next(session_iter), term, offset, size): (offset, size)
                for term, offset, size in batch_args
            }
            
            # Collect results
            for future in as_completed(future_to_batch):
                batch_data = future.result()
                courses.extend(batch_data)
                completed_batches += 1
                print(f"Course batches: {completed_batches}/{len(batch_args)} complete")
        
        print(f"Successfully fetched {len(courses)} courses")
        
        # Fetch prerequisites in parallel if requested
        if include_prerequisites:
            prerequisites = self.fetch_prerequisites_parallel(courses, term, session)
            
            # Add prerequisites to course data
            for course in courses:
                crn = course.get("courseReferenceNumber")
                if crn and crn in prerequisites:
                    course["prerequisites"] = prerequisites[crn]
                else:
                    course["prerequisites"] = ""
        
        total_time = time.time() - start_time
        print(f"Total execution time: {total_time:.1f}s")
        
        return courses


def fetch_course_data(term: str = "202440", include_prerequisites: bool = True, 
                     max_workers: int = 20, batch_size: int = 500, 
                     course_batch_workers: int = 20) -> List[Dict]:
    """
    Convenience function to fetch course data with default parallelization settings.
    
    Args:
        term: Term code (e.g., "202440" for Fall 2024)
        include_prerequisites: Whether to fetch prerequisite information
        max_workers: Maximum concurrent threads for prerequisite fetching
        batch_size: Number of courses per batch
        course_batch_workers: Concurrent workers for course batch fetching
    
    Returns:
        List of course dictionaries
    """
    fetcher = UCRCourseFetcher(max_workers=max_workers)
    return fetcher.fetch_course_data_parallel(
        term=term, 
        include_prerequisites=include_prerequisites, 
        batch_size=batch_size,
        course_batch_workers=course_batch_workers
    )


if __name__ == "__main__":
    # Example usage with different concurrency levels
    print("Fetching with default settings (20 workers)...")
    courses = fetch_course_data()
    print(f"Fetched {len(courses)} courses")
    
    # Example with more aggressive parallelization
    # print("Fetching with high concurrency (50 workers)...")
    # courses = fetch_course_data(max_workers=50, course_batch_workers=5)
    # print(f"Fetched {len(courses)} courses")