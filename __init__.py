import re
import requests
import numpy as np

def calculate_resolution(pixel_count, aspect_ratio):
    pixel_count = pixel_count / 4096
    w, h = aspect_ratio
    k = (pixel_count * w / h) ** 0.5
    width = int(np.floor(k) * 64)
    height = int(np.floor(k * h / w) * 64)
    return width, height

class TagFromDanbooruUrl:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "danbooru_url": ("STRING", { "default": "https://danbooru.donmai.us/posts/", "multiline": True, "dynamicPrompts": False }),
                "additional_tags": ("STRING", { "default": "highres, very detailed, masterpiece, very aesthetic", "multiline": True, "dynamicPrompts": False }),
                "add_character": ("BOOLEAN", { "default": True }),
                "add_artist": ("BOOLEAN", { "default": True }),
                "add_rating": ("BOOLEAN", { "default": True }),
            },
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("tags", "width", "height")
    FUNCTION = "fetchTags"
    CATEGORY = "utils"
    def fetchTags(self, danbooru_url, additional_tags, add_artist, add_character, add_rating):
        if danbooru_url:
            try:
                if "danbooru.donmai.us/posts" not in danbooru_url:
                    return ("unsupported url",)
                if "?" in danbooru_url:
                    pos = danbooru_url.find("?")
                    danbooru_url = danbooru_url[:pos]
                url = danbooru_url + ".json"

                with requests.get(url, headers={
                    'user-agent': 'my-app/0.0.1'}) as r:  # it needs a user agent otherwise it doesn't work
                    data = r.json()
                    rating = data["rating"]
                    artist = data["tag_string_artist"]
                    char = data["tag_string_character"]
                    copyright = data["tag_string_copyright"]
                    general_tags = data["tag_string_general"].split(" ")
                    width = data["image_width"]
                    height = data["image_height"]

                r = re.compile(r'[1-6][+]*(boy|girl)[s]*')
                boys_and_girls = list(filter(r.match, general_tags))
                remain_tags = [x for x in general_tags if (x not in boys_and_girls)]
                format_tags = " ".join(boys_and_girls)

                rating_table = { "g": "general", "s": "sensitive", "q": "questionable", "e": "explicit" }
                if add_character and char:
                    format_tags += " " + char
                if add_character and copyright:
                    format_tags += " " + copyright
                if add_artist and artist:
                    format_tags += " " + artist
                if add_rating and rating:
                    format_tags += " " + rating_table[rating]

                format_tags += " " + " ".join(remain_tags)
                format_tags = format_tags.strip().replace(" ", ", ").replace("_", " ") \
                        .replace("(", "\(").replace(")", "\)").replace("[", "\[").replace("]", "\]")
                format_tags = ", ".join([format_tags, additional_tags])
                (w, h) = calculate_resolution(1024*1024, (width, height))

                return (format_tags, w, h,)

            except Exception as err:
                raise err
        else:
            return ("",)


NODE_CLASS_MAPPINGS = { "TagFromDanbooruUrl": TagFromDanbooruUrl }
NODE_DISPLAY_NAME_MAPPINGS = { "TagFromDanbooruUrl": "Tag from Danbooru url" }
