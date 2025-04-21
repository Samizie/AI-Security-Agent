from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import GithubSearchTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class AuditorAgent():
    """
    Auditor Agent for AI Auditor
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def repo_cloner(self) -> Agent:
        return Agent(
            config=self.agents_config['repo_cloner'],
            verbose=True,
            tools=[]
        )