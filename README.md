# ChatGPT to CSV

**Live App:** https://chatgpt-to-csv.streamlit.app/

__ChatGPT to CSV__ is a web application that converts ChatGPT export files into structured CSV datasets. It extracts conversations from the official ChatGPT export format and flattens them into a message-level table that can be more easily analyzed.

The application is designed to make ChatGPT conversation data easier to work with for research, data analysis, and archiving.

## Output Format

Each row in the output CSV represents **one message** from a ChatGPT conversation.

| Column | Description |
|------|-------------|
| `conversation_id` | Unique identifier from the original ChatGPT export |
| `conversation_simple_id` | Sequential ID assigned during processing |
| `conversation_title` | Title of the conversation |
| `role` | Message author (`User` or `AI`) |
| `message_index` | Order of the message within the conversation |
| `datetime` | Timestamp converted to a readable format |
| `message` | Text content of the message |

Example output:

```csv
conversation_id,conversation_simple_id,conversation_title,role,message_index,datetime,message
abc123,1,"Research ideas",User,1,"Mar 10, 2026 10:14","How could I study the effects of exercise on depression?"
abc123,1,"Research ideas",AI,2,"Mar 10, 2026 10:14","One approach would be to analyze..."
