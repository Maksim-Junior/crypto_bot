from selenium import webdriver
from db import search_currency, id_for_parser


class CryptoParse:
    def __init__(self, url, bot=None):
        self.driver = webdriver.Chrome()
        self.driver.minimize_window()
        self.url = url
        self.bot = bot

    def __del__(self):
        self.driver.close()

    async def parse(self):
        all_id = await id_for_parser()
        print(self.url)
        self.driver.get(self.url)
        btc_item = self.driver.find_element_by_id("fullColumn")
        btc_itemz = btc_item.find_element_by_css_selector("tbody")
        data = btc_itemz.text
        row_list = data.split("\n")
        row_dict = {}
        done_data = []
        for i in range(100):
            row_dict[i] = row_list[i].split(" ")
        for key in row_dict:
            item = row_dict[key]
            cur_list_two = [
                "Binance", "USD", "Internet", "Bitcoin", "Эфириум", "Wrapped", "SHIBA", "FTX", "Crypto.com", "Huobi",
                "Hedera", "Theta", "Enjin", "Paxos", "NEAR", "OMG", "The",
            ]
            cur_list_three = ["UNUS", "Basic", "Curve"]
            if item[1] in cur_list_two:
                if (item[1] == "Эфириум" and item[2] == "Классик") or item[1] != "Эфириум":
                    if "." in item[4]:
                        item[4] = item[4].replace(".", "")
                    if "," in item[4]:
                        item[4] = item[4].replace(",", ".")
                    number = float(item[4])
                    text = f"{item[3]} - {round(number, 2)} $"
                else:
                    if "." in item[3]:
                        item[3] = item[3].replace(".", "")
                    if "," in item[3]:
                        item[3] = item[3].replace(",", ".")
                    number = float(item[3])
                    text = f"{item[2]} - {round(number, 2)} $"
            elif item[1] in cur_list_three:
                if "." in item[5]:
                    item[5] = item[5].replace(".", "")
                if "," in item[5]:
                    item[5] = item[5].replace(",", ".")
                number = float(item[5])
                text = f"{item[4]} - {round(number, 2)} $"
            else:
                if "." in item[3]:
                    item[3] = item[3].replace(".", "")
                if "," in item[3]:
                    item[3] = item[3].replace(",", ".")
                number = float(item[3])
                text = f"{item[2]} - {round(number, 2)} $"
            done_data.append(text)
        dict_answer = {}
        for chat_id in all_id:
            answer = ''
            ans = ''
            dict_answer[chat_id] = 0
            data_user = await search_currency(chat_id)
            currency = {}
            for user in data_user:
                currency[user.currency] = user.price
            for key in currency:
                for j in done_data:
                    cur = j.split(" ")
                    if key == cur[0]:
                        ans = j
                        if currency[key] != "-1":
                            user_bought = float(currency[key])
                            now_price = float(cur[2])
                            percent = ((now_price * 100) / user_bought) - 100
                            if percent >= 0:
                                ans += f' (+{round(percent, 3)}%)'
                            else:
                                ans += f' ({round(percent, 3)}%)'
                answer += f'{ans}\n'
            if answer:
                dict_answer[chat_id] = answer
        for key in dict_answer:
            if dict_answer[key] != 0:
                await self.bot.send_message(chat_id=key, text=dict_answer[key])
