from pprint import pprint
import requests
import json


class VK:

    API_base_url = "https://api.vk.ru/method/"

    def __init__(self, access_token, user_id, Jy_token, version='5.131'):

        self.token = access_token
        self.id = user_id
        self.Jy_token = Jy_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()
    
    def get_profile_photo(self):
        params = self.params
        params.update({"owner_id": self.id, "album_id": "profile", "extended": 1})
        response = requests.get(f'{self.API_base_url}photos.get', params=params)
        return response.json()['response']['items']
    
    def JA_save(self):
        headers = {"Authorization": f'OAuth {self.Jy_token}'}
        params = {"path": "profile_photo"}
        response = requests.put("https://cloud-api.yandex.net/v1/disk/resources", 
                                headers=headers, 
                                params=params)
        info = {"info": []}
        count_photo = 0
        for photo in self.get_profile_photo():
            max_size = -100
            for i in photo['sizes']:
                max_size = max(max_size, i['height']+i['width'])
            for i in photo['sizes']:
                if i['height']+i['width'] == max_size:
                    image_name = photo['likes']['count']
                    file = i['url']
                    params = {'url': file, 'path': f"profile_photo/{image_name}.jpg"}
                    response = requests.post("https://cloud-api.yandex.net/v1/disk/resources/upload", 
                                            headers=headers,
                                            params=params)
                    count_photo += 1
                    info['info'].append({"file_name": f"{image_name}.jpg", "size": i['type']})
                    print(f'Файл {image_name}.jpg загружен. Всего загружено файлов: {count_photo}.')

        response = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload", 
                                            headers=headers,
                                            params={'path': f'profile_photo/Info.json'}) 
        url = response.json()["href"] 
        with open("Info.json", "w") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        with open("Info.json", "rb") as f:
            requests.put(url, files={'file': f})
        return info            


if __name__ == "__main__":
    access_token = input("Введите ваш access_token ВК")
    user_id = int(input("Введите ваш user_id ВК"))
    Jy_token = input("Введите ваш токен с Полигона Яндекс.Диска")
    vk_client = VK(access_token, user_id, Jy_token)
    pprint(vk_client.JA_save())

