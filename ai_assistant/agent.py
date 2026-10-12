import json

from openai import OpenAI
from django.conf import settings

from .prompts import SYSTEM_PROMPT
from .tools import (
    get_my_profile,
    search_internships,
    get_internship_details,
    get_my_applications,
    get_application_status,
    get_learning_resource,
)


# ============================================================
# OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
)


# ============================================================
# AI TOOLS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_my_profile",
            "description": (
                "Get the authenticated student's profile, "
                "including program, skills, interests, "
                "university, and preferred location."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
{
    "type": "function",
    "function": {
        "name": "get_learning_resource",
        "description": (
            "Generate a YouTube search link for learning any "
            "topic requested by the student. The topic can be "
            "programming, business, accounting, marketing, "
            "design, communication, mathematics, science, "
            "career skills, or any other educational subject."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": (
                        "The subject or skill the student wants "
                        "to learn, such as Python, accounting, "
                        "marketing, graphic design, or public speaking."
                    ),
                },
                "level": {
                    "type": "string",
                    "description": (
                        "The student's learning level if known. "
                        "Examples: beginner, intermediate, advanced."
                    ),
                    "enum": [
                        "beginner",
                        "intermediate",
                        "advanced"
                    ],
                    "default": "beginner",
                },
            },
            "required": ["topic"],
            "additionalProperties": False,
        },
    },
},

    {
        "type": "function",
        "function": {
            "name": "search_internships",
            "description": (
                "Search active internship opportunities "
                "by field, location, or required skill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "field": {
                        "type": "string",
                        "description": "Internship field.",
                    },
                    "location": {
                        "type": "string",
                        "description": "Preferred location.",
                    },
                    "skill": {
                        "type": "string",
                        "description": "Required skill.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_internship_details",
            "description": (
                "Get detailed information about "
                "one active internship."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "internship_id": {
                        "type": "integer",
                        "description": "The internship ID.",
                    },
                },
                "required": [
                    "internship_id",
                ],
                "additionalProperties": False,
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_my_applications",
            "description": (
                "Get the authenticated student's "
                "internship applications."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },

    {
        "type": "function",
        "function": {
            "name": "get_application_status",
            "description": (
                "Get the status of one application "
                "belonging to the authenticated student."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "integer",
                        "description": "The application ID.",
                    },
                },
                "required": [
                    "application_id",
                ],
                "additionalProperties": False,
            },
        },
    },
]


# ============================================================
# TOOL FUNCTIONS
# ============================================================

TOOL_FUNCTIONS = {
    "get_my_profile": get_my_profile,
    "search_internships": search_internships,
    "get_internship_details": get_internship_details,
    "get_my_applications": get_my_applications,
    "get_application_status": get_application_status,
    "get_learning_resource": get_learning_resource,
}

# ============================================================
# RUN AGENT
# ============================================================

def run_agent(user, message):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    learning_url = None

    # --------------------------------------------------------
    # TOOL-CALL LOOP
    # --------------------------------------------------------

    for iteration in range(5):

        print(f"\nAGENT ITERATION {iteration + 1}/5")

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=TOOLS,
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls or []

        print("FINISH REASON:", response.choices[0].finish_reason)
        print("AI CONTENT:", assistant_message.content)
        print("TOOL CALL COUNT:", len(tool_calls))

        # ----------------------------------------------------
        # MODEL HAS FINISHED
        # ----------------------------------------------------

        if not tool_calls:

            return {
                "message": (
                    assistant_message.content
                    or "I couldn't generate a response."
                ),
                "learning_url": learning_url,
            }

        # ----------------------------------------------------
        # SAVE ASSISTANT TOOL CALLS
        # ----------------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in tool_calls
                ],
            }
        )

        # ----------------------------------------------------
        # EXECUTE TOOLS
        # ----------------------------------------------------

        for tool_call in tool_calls:

            tool_name = tool_call.function.name
            raw_arguments = tool_call.function.arguments

            print("EXECUTING TOOL:", tool_name)
            print("RAW ARGUMENTS:", raw_arguments)

            tool_function = TOOL_FUNCTIONS.get(tool_name)

            if tool_function is None:

                tool_result = {
                    "error": f"Unknown tool: {tool_name}"
                }

            else:

                try:
                    arguments = json.loads(raw_arguments or "{}")

                    if not isinstance(arguments, dict):
                        raise ValueError(
                            "Tool arguments must be a JSON object."
                        )

                except (json.JSONDecodeError, TypeError, ValueError) as e:

                    print("ARGUMENT ERROR:", str(e))

                    tool_result = {
                        "error": "Invalid tool arguments."
                    }

                else:

                    try:
                        tool_result = tool_function(
                            user,
                            **arguments,
                        )

                    except Exception as e:

                        import traceback

                        print("TOOL ERROR:", tool_name, str(e))
                        traceback.print_exc()

                        tool_result = {
                            "error": str(e)
                        }

            print("TOOL RESULT:", repr(tool_result))

            # Capture learning resource URL
            if tool_name == "get_learning_resource":
                if isinstance(tool_result, dict):
                    learning_url = (
                        tool_result.get("url")
                        or tool_result.get("learning_url")
                    )

            # Send tool result back to model
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        default=str,
                    ),
                }
            )

    # --------------------------------------------------------
    # FINAL ANSWER: DO NOT ALLOW MORE TOOL CALLS
    # --------------------------------------------------------

    print("TOOL LIMIT REACHED. REQUESTING FINAL ANSWER.")

    final_messages = messages + [
        {
            "role": "system",
            "content": (
                "You must now provide your final response to the user. "
                "Do not request or call any tools. Review all tool results "
                "in the conversation. Summarize the relevant internships, "
                "explain when no results matched a search, and be honest "
                "about missing information. Do not claim you performed "
                "actions that are not shown in the tool results."
            ),
        }
    ]

    try:

        final_response = client.chat.completions.create(
            model="openrouter/free",
            messages=final_messages,
        )

        final_message = (
            final_response.choices[0].message.content
        )

        print("FINAL FINISH REASON:",
              final_response.choices[0].finish_reason)
        print("FINAL AI RESPONSE:", final_message)

        if final_message and final_message.strip():

            return {
                "message": final_message,
                "learning_url": learning_url,
            }

    except Exception as e:

        import traceback

        print("FINAL RESPONSE ERROR:", str(e))
        traceback.print_exc()

    # --------------------------------------------------------
    # LAST RESORT
    # --------------------------------------------------------

    return {
        "message": (
            "I found some information, but couldn't prepare a final "
            "answer. Please try again."
        ),
        "learning_url": learning_url,
    }