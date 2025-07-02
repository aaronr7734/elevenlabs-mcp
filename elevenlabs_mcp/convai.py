def create_conversation_config(
    language: str,
    system_prompt: str,
    llm: str,
    first_message: str | None,
    temperature: float,
    max_tokens: int | None,
    asr_quality: str,
    voice_id: str | None,
    model_id: str,
    optimize_streaming_latency: int,
    stability: float,
    similarity_boost: float,
    turn_timeout: int,
    max_duration_seconds: int,
) -> dict:
    return {
        "agent": {
            "language": language,
            "prompt": {
                "prompt": system_prompt,
                "llm": llm,
                "tools": [{"type": "system", "name": "end_call", "description": ""}],
                "knowledge_base": [],
                "temperature": temperature,
                **({"max_tokens": max_tokens} if max_tokens else {}),
            },
            **({"first_message": first_message} if first_message else {}),
            "dynamic_variables": {"dynamic_variable_placeholders": {}},
        },
        "asr": {
            "quality": asr_quality,
            "provider": "elevenlabs",
            "user_input_audio_format": "pcm_16000",
            "keywords": [],
        },
        "tts": {
            **({"voice_id": voice_id} if voice_id else {}),
            "model_id": model_id,
            "agent_output_audio_format": "pcm_16000",
            "optimize_streaming_latency": optimize_streaming_latency,
            "stability": stability,
            "similarity_boost": similarity_boost,
        },
        "turn": {"turn_timeout": turn_timeout},
        "conversation": {
            "max_duration_seconds": max_duration_seconds,
            "client_events": [
                "audio",
                "interruption",
                "user_transcript",
                "agent_response",
                "agent_response_correction",
            ],
        },
        "language_presets": {},
        "is_blocked_ivc": False,
        "is_blocked_non_ivc": False,
    }


def create_platform_settings(
    record_voice: bool,
    retention_days: int,
) -> dict:
    return {
        "widget": {
            "variant": "full",
            "avatar": {"type": "orb", "color_1": "#6DB035", "color_2": "#F5CABB"},
            "feedback_mode": "during",
            "terms_text": '#### Terms and conditions\n\nBy clicking "Agree," and each time I interact with this AI agent, I consent to the recording, storage, and sharing of my communications with third-party service providers, and as described in the Privacy Policy.\nIf you do not wish to have your conversations recorded, please refrain from using this service.',
            "show_avatar_when_collapsed": True,
        },
        "evaluation": {},
        "auth": {"allowlist": []},
        "overrides": {},
        "call_limits": {"agent_concurrency_limit": -1, "daily_limit": 100000},
        "privacy": {
            "record_voice": record_voice,
            "retention_days": retention_days,
            "delete_transcript_and_pii": True,
            "delete_audio": True,
            "apply_to_existing_conversations": False,
        },
        "data_collection": {},
    }


def build_conversation_override(
    current_prompt: str | None = None,
    append_to_prompt: str | None = None,
    first_message: str | None = None,
):
    """Build conversation override with system prompt and/or first message modifications.

    Args:
        current_prompt: Current agent system prompt (required if append_to_prompt is provided)
        append_to_prompt: Text to append to the system prompt (optional)
        first_message: Override first message (optional)

    Returns:
        ConversationInitiationClientDataRequestInput: Override configuration
    """
    from elevenlabs.types.conversation_initiation_client_data_request_input import (
        ConversationInitiationClientDataRequestInput,
    )
    from elevenlabs.types.conversation_config_client_override_input import (
        ConversationConfigClientOverrideInput,
    )
    from elevenlabs.types.agent_config_override import AgentConfigOverride
    from elevenlabs.types.prompt_agent_api_model_override import (
        PromptAgentApiModelOverride,
    )

    # Build agent override if needed
    agent_override_params = {}

    # Handle system prompt override
    if append_to_prompt and current_prompt:
        combined_prompt = f"{current_prompt}\n\n{append_to_prompt}"
        agent_override_params["prompt"] = PromptAgentApiModelOverride(
            prompt=combined_prompt
        )

    # Handle first message override
    if first_message is not None:
        agent_override_params["first_message"] = first_message

    if not agent_override_params:
        return None

    # Build the override structure
    agent_override = AgentConfigOverride(**agent_override_params)
    conversation_config_override = ConversationConfigClientOverrideInput(
        agent=agent_override
    )

    return ConversationInitiationClientDataRequestInput(
        conversation_config_override=conversation_config_override
    )
