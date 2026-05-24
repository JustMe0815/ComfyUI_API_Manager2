import os
import json
import requests

class PostImageToAPI:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Changed from "IMAGE" tensor to "STRING" file paths from your Save Node
                "file_paths": ("STRING", {"forceInput": True}), 
                "api_url": ("STRING", {"default": ""}),
                "api_object_id": ("STRING", {"forceInput": True}),
                "api_key": ("STRING", {"forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("api_response",)
    FUNCTION = "post_images"
    CATEGORY = "API Manager"
    OUTPUT_NODE = True

    def post_images(self, file_paths, api_url, api_object_id, api_key=""):
        # Handle string/list conversions for ComfyUI batching
        if isinstance(api_object_id, list):
            api_object_id = str(api_object_id[0]) if api_object_id else ""
        if isinstance(api_key, list):
            api_key = str(api_key[0]) if api_key else ""
        if isinstance(api_url, list):
            api_url = str(api_url[0]) if api_url else ""

        api_object_id = str(api_object_id).strip("[]'\"")
        api_key = str(api_key).strip("[]'\"")
        api_url = str(api_url).strip("[]'\"")

        # Dynamically build the target endpoint path
        api_url = api_url.replace("{slug}", api_object_id).replace("$id", api_object_id)
        headers = {'X-API-Key': api_key} if api_key else {}
        results = []

        # If ComfyUI bundles multiple file paths as a list or a list inside a list
        paths_to_process = []
        if isinstance(file_paths, list):
            for path in file_paths:
                if isinstance(path, list):
                    paths_to_process.extend(path)
                else:
                    paths_to_process.append(path)
        else:
            paths_to_process.append(file_paths)

        for path in paths_to_process:
            path = str(path).strip("[]'\"")
            if not path or not os.path.exists(path):
                results.append(f"Skipped: Path invalid or file not found: '{path}'")
                continue

            # Extract the original filename (e.g., "Urban_Wanderer_..._01.jpg")
            filename = os.path.basename(path)
            
            # Detect MIME type based on extension
            mime_type = 'image/png' if filename.lower().endswith('.png') else 'image/jpeg'

            try:
                with open(path, 'rb') as f:
                    # 'file' is the key Grav expects, but we pass the actual original filename as the second parameter
                    files = {'file': (filename, f.read(), mime_type)}
                    response = requests.post(api_url, headers=headers, files=files)
                    
                if response.status_code in [200, 201]:
                    results.append(f"Success ({filename}): Uploaded.")
                else:
                    results.append(f"Error ({filename}) [{response.status_code}]: {response.text}")
            except Exception as e:
                results.append(f"Exception uploading {filename}: {str(e)}")

        output_status = "\n".join(results)
        print(f"PostImageToAPI Output:\n{output_status}")
        
        return (output_status,)
