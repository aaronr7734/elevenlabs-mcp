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


def build_updated_conversation_config(
    existing_config,
    system_prompt: str | None = None,
    first_message: str | None = None,
    voice_id: str | None = None,
    language: str | None = None,
    llm: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    asr_quality: str | None = None,
    model_id: str | None = None,
    optimize_streaming_latency: int | None = None,
    stability: float | None = None,
    similarity_boost: float | None = None,
    turn_timeout: int | None = None,
    max_duration_seconds: int | None = None,
) -> dict:
    """Build updated conversation config from existing config and new parameters.

    Args:
        existing_config: Current conversation configuration
        **kwargs: Optional parameters to update

    Returns:
        dict: Updated conversation configuration
    """
    return create_conversation_config(
        language=language or existing_config.agent.language,
        system_prompt=system_prompt or existing_config.agent.prompt.prompt,
        llm=llm or existing_config.agent.prompt.llm,
        first_message=first_message
        or getattr(existing_config.agent, "first_message", None),
        temperature=temperature
        if temperature is not None
        else existing_config.agent.prompt.temperature,
        max_tokens=max_tokens
        if max_tokens is not None
        else getattr(existing_config.agent.prompt, "max_tokens", None),
        asr_quality=asr_quality or existing_config.asr.quality,
        voice_id=voice_id or getattr(existing_config.tts, "voice_id", None),
        model_id=model_id or existing_config.tts.model_id,
        optimize_streaming_latency=optimize_streaming_latency
        if optimize_streaming_latency is not None
        else existing_config.tts.optimize_streaming_latency,
        stability=stability if stability is not None else existing_config.tts.stability,
        similarity_boost=similarity_boost
        if similarity_boost is not None
        else existing_config.tts.similarity_boost,
        turn_timeout=turn_timeout
        if turn_timeout is not None
        else existing_config.turn.turn_timeout,
        max_duration_seconds=max_duration_seconds
        if max_duration_seconds is not None
        else existing_config.conversation.max_duration_seconds,
    )


def build_updated_platform_settings(
    existing_settings,
    record_voice: bool | None = None,
    retention_days: int | None = None,
) -> dict:
    """Build updated platform settings from existing settings and new parameters.

    Args:
        existing_settings: Current platform settings
        record_voice: New voice recording setting (optional)
        retention_days: New data retention setting (optional)

    Returns:
        dict: Updated platform settings
    """
    return create_platform_settings(
        record_voice=record_voice
        if record_voice is not None
        else existing_settings.privacy.record_voice,
        retention_days=retention_days
        if retention_days is not None
        else existing_settings.privacy.retention_days,
    )


def build_system_prompt_override(
    current_prompt: str,
    append_text: str,
):
    """Build conversation override with appended system prompt.

    Args:
        current_prompt: Current agent system prompt
        append_text: Text to append to the system prompt

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

    # Create the combined prompt
    combined_prompt = f"{current_prompt}\n\n{append_text}"

    # Build the override structure
    prompt_override = PromptAgentApiModelOverride(prompt=combined_prompt)
    agent_override = AgentConfigOverride(prompt=prompt_override)
    conversation_config_override = ConversationConfigClientOverrideInput(
        agent=agent_override
    )

    return ConversationInitiationClientDataRequestInput(
        conversation_config_override=conversation_config_override
    )
