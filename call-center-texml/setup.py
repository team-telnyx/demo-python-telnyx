"""
Run on setup of project

"""

env_vars = """API_KEY=
PROD=True
SLACK_URL=
NGROK_URL=
"""


def main():
    env_file = open("call_center/.env", "w+")
    env_file.write(env_vars)


if __name__ == "__main__":
    main()