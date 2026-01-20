import inspect
import os
import json
from fastapi import HTTPException
from pprint import pformat

def var_dump_die(data):
    # Get the caller information
    frame = inspect.stack()[1]
    file_path = frame.filename
    line_no = frame.lineno
    function_name = frame.function
    file_name = os.path.basename(file_path)

    # Safely format data (in case it's not JSON-serializable)
    try:
        formatted_data = json.loads(json.dumps(data, default=str))
    except Exception:
        formatted_data = pformat(data, width=100)

    # Build structured debug payload
    debug_payload = {
        "debug": True,
        "location": {
            "file": file_name,
            "line": line_no,
            "function": function_name,
        },
        "data": formatted_data
    }

    # Pretty-print JSON (for logs)
    print(json.dumps(debug_payload, indent=4, ensure_ascii=False))

    # Raise an HTTPException with JSON detail
    raise HTTPException(status_code=400, detail=debug_payload)
