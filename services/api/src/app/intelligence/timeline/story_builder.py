from app.intelligence.prompts.base import BasePrompt, PromptMetadata, PromptVersion


class TimelineNarratorPrompt(BasePrompt):
    """Structured prompt template for the Timeline Narrator Agent."""

    def __init__(self) -> None:
        metadata = PromptMetadata(
            name="timeline_narrator_agent",
            description="Converts raw chronological events into structured stories across operations, security, medical, crowd, and volunteer timelines.",
            author="System",
            tags=["agent", "narrator", "timeline"],
        )
        versions = [
            PromptVersion(
                version="v1",
                template=(
                    "You are the ATLAS Stadium Operations Timeline Narrator Agent.\n"
                    "Convert the following raw operational logs into a human-readable operational story.\n"
                    "Your response must be in the language: {language}\n"
                    "Your narrative style must be: {style}\n"
                    "Raw Operational Logs:\n"
                    "{formatted_logs}\n\n"
                    "Convert the events into a narrative history. Instead of raw log codes, write flow statements.\n"
                    "Compile specific timelines: Executive, Security, Medical, Crowd, and Volunteer.\n"
                    "Format your response to match the requested schema.\n"
                )
            )
        ]
        super().__init__(metadata, versions)
