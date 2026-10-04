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

    # Store URL returned by learning-resource tool
    learning_url = None

    # --------------------------------------------------------
    # Allow several tool calls / conversation turns
    # --------------------------------------------------------

    for _ in range(5):

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=TOOLS,
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # No tool call
        # ----------------------------------------------------

        if not assistant_message.tool_calls:

            return {
                "message": (
                    assistant_message.content
                    or "I couldn't generate a response."
                ),
                "learning_url": learning_url,
            }

        # ----------------------------------------------------
        # Add assistant tool-call message
        # ----------------------------------------------------

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in assistant_message.tool_calls
                ],
            }
        )

        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            tool_arguments_raw = (
                tool_call.function.arguments
            )

            # -----------------------------------------------
            # Check that tool exists
            # -----------------------------------------------

            tool_function = TOOL_FUNCTIONS.get(
                tool_name
            )

            if tool_function is None:

                tool_result = {
                    "error": f"Unknown tool: {tool_name}"
                }

            else:

                # -------------------------------------------
                # Parse arguments
                # -------------------------------------------

                try:

                    arguments = json.loads(
                        tool_arguments_raw or "{}"
                    )

                except (
                    json.JSONDecodeError,
                    TypeError,
                ):

                    tool_result = {
                        "error": (
                            "The AI provided invalid "
                            "tool arguments."
                        )
                    }

                else:

                    # ---------------------------------------
                    # Execute Django tool
                    # ---------------------------------------

                    try:

                        tool_result = tool_function(
                            user,
                            **arguments,
                        )

                    except Exception as e:

                        print(
                            "============================================"
                        )

                        print("AI TOOL ERROR")

                        print(
                            "Tool:",
                            tool_name
                        )

                        print(
                            "Error:",
                            e
                        )

                        print(
                            "Type:",
                            type(e).__name__
                        )

                        print(
                            "============================================"
                        )

                        import traceback

                        traceback.print_exc()

                        tool_result = {
                            "error": str(e)
                        }

            # ------------------------------------------------
            # Capture learning-resource URL
            # ------------------------------------------------

            if tool_name == "get_learning_resource":

                if isinstance(
                    tool_result,
                    dict
                ):

                    learning_url = (
                        tool_result.get("url")
                        or tool_result.get("learning_url")
                    )

            # ------------------------------------------------
            # Send tool result back to AI
            # ------------------------------------------------

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
    # Prevent infinite tool loops
    # --------------------------------------------------------

    return {
        "message": (
            "I wasn't able to complete the request. "
            "Please try again."
        ),
        "learning_url": learning_url,
    }
