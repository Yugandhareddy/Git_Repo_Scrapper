import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd

# List of topics
topics = [
    "3d", "ajax", "algorithm", "android", "angular", "animation", "api",
    "arduino", "artificial-intelligence", "aspnet", "atom", "awesome-list",
    "aws", "azure", "babel", "backend", "bash", "bitcoin", "blockchain",
    "bootstrap", "bot", "c", "chrome", "chrome-extension", "cli", "clojure",
    "code-quality", "code-review", "compiler", "continuous-integration",
    "covid-19", "csharp", "css", "cybersecurity", "dart", "data-science",
    "deep-learning", "deno", "devops", "django", "docker", "documentation",
    "dotnet", "drupal", "electron", "elixir", "elm", "ember", "emulator",
    "es6", "eslint", "ethereum", "express", "facebook", "firebase", "firefox",
    "flask", "flutter", "font", "framework", "game", "game-engine", "git",
    "github", "go", "godot", "google", "google-cloud", "gradle", "graphql",
    "haskell", "haxl", "hbase", "home-assistant", "html", "html5", "http",
    "icon", "ios", "iot", "ipfs", "java", "javascript", "jekyll", "jenkins",
    "julia", "jupyter", "kafka", "keras", "kotlin", "kubernetes", "language",
    "laravel", "learning", "library", "linux", "lua", "machine-learning",
    "macos", "markdown", "mastodon", "material", "microservices", "mongodb",
    "monitoring", "music", "mysql", "natural-language-processing",
    "neural-network", "nextjs", "nlp", "nodejs", "nosql", "numpy", "objective-c",
    "opensource", "pandas", "parsing", "perl", "php", "plugin", "postgresql",
    "powershell", "programming", "project-management", "publishing", "pwa",
    "python", "pytorch", "qt", "r", "react", "react-native", "redux",
    "reinforcement-learning", "rest", "ruby", "rust", "sass", "scala", "scripting",
    "sdk", "security", "server", "serverless", "shopify", "sketch", "slack",
    "software", "spark", "spring", "sql", "sql-server", "ssl", "statistics",
    "swift", "telegram", "tensorflow", "terminal", "testing", "twitter", "typescript",
    "ubuntu", "ui", "unity", "unreal-engine", "vagrant", "vim", "virtual-reality",
    "visualization", "vue", "web", "web-components", "webapp", "webpack",
    "website", "windows", "wordpress", "xamarin", "xml", "yaml", "youtube"
]

@st.cache_data
def scrape_github_repositories(user_name):
    """Scrape all repositories from a given GitHub user's profile."""
    page_number = 1
    base_url = 'https://github.com'
    repos = []
    repo_index = 1

    while True:
        url = f"https://github.com/{user_name}?page={page_number}&tab=repositories"
        response = requests.get(url)

        if response.status_code != 200:
            st.error("Failed to retrieve the page. Please check the URL and try again.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        repo_divs = soup.findAll('div', class_='d-inline-block mb-1')

        if not repo_divs:
            break

        for repo_div in repo_divs:
            a_tag = repo_div.find('a')
            if a_tag:
                repo_url = base_url + a_tag['href']
                description_tag = repo_div.find_next('p')
                description = description_tag.text.strip() if description_tag else 'No description'
                
                stars_tag = repo_div.find_next('a', class_='Link--muted')
                if stars_tag:
                    stars_text = stars_tag.text.strip().replace(',', '')
                    try:
                        stars = int(stars_text)
                    except ValueError:
                        stars = 0
                else:
                    stars = 0

                repos.append((repo_index, a_tag.text.strip(), repo_url, description, stars))
                repo_index += 1

        page_number += 1

    return repos

@st.cache_data
def scrape_repositories_by_topic(topic):
    """Scrape repositories for a given topic from GitHub topics page."""
    url = f"https://github.com/topics/{topic}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to retrieve repositories. Please try again later.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    repo_elements = soup.find_all('article', class_='border rounded color-shadow-small color-bg-subtle my-4')
    repos = []

    for repo_element in repo_elements:
        title_element = repo_element.find('h3', class_='f3 color-fg-muted text-normal lh-condensed')
        if title_element:
            anchors = title_element.find_all('a')
            if len(anchors) == 2:
                owner_name = anchors[0].text.strip()
                repo_name = anchors[1].text.strip()
                full_repo_name = f"{owner_name}/{repo_name}"
                repo_url = f"https://github.com{anchors[1]['href']}"
                description_element = repo_element.find('p', class_='color-fg-muted my-1 pr-4')
                description = description_element.text.strip() if description_element else "No description"
                stars_element = repo_element.find('a', class_='Link--muted d-inline-block mr-3')
                stars = int(stars_element.text.strip().replace(',', '')) if stars_element else 0

                repos.append((full_repo_name, repo_url, description, stars))

    return repos

# Streamlit application
def main():
    st.set_page_config(page_title="GitHub Repository Explorer", page_icon=":rocket:", layout="wide")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    selected_feature = st.sidebar.radio("Select a feature", ["Scrape User Repositories", "Explore Topics"])

    # Page content
    st.title("GitHub Repository Explorer")

    if selected_feature == "Scrape User Repositories":
        st.header("Scrape User Repositories")
        user_name = st.text_input("Enter the GitHub username")
        
        if st.button("Scrape User Repositories"):
            if user_name:
                with st.spinner('Scraping repositories...'):
                    repos = scrape_github_repositories(user_name)

                if repos:
                    df = pd.DataFrame(repos, columns=['Index', 'Repository Name', 'Repository URL', 'Description', 'Stars'])

                    min_stars = st.slider('Minimum stars', 0, 1000, 0)
                    df = df[df['Stars'] >= min_stars]

                    st.dataframe(df)

                    csv = df.to_csv(index=False)
                    st.download_button(label="Download CSV", data=csv, file_name=f'{user_name}_repositories.csv', mime='text/csv')
                else:
                    st.warning("No repositories found.")

    elif selected_feature == "Explore Topics":
        st.header("Explore Topics")
        selected_topic = st.selectbox("Select a topic", topics)
        
        if st.button("Get Topic Repositories"):
            with st.spinner(f"Scraping repositories for {selected_topic}..."):
                repos = scrape_repositories_by_topic(selected_topic)

            if repos:
                df = pd.DataFrame(repos, columns=['Repository Name', 'Repository URL', 'Description', 'Stars'])

                min_stars = st.slider('Minimum stars', 0, 1000, 0)
                df = df[df['Stars'] >= min_stars]

                st.dataframe(df)

                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV", data=csv, file_name=f'{selected_topic}_repositories.csv', mime='text/csv')
            else:
                st.warning("No repositories found.")

if __name__ == "__main__":
    main()

