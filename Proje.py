from bs4 import BeautifulSoup
from tkinter import *
from tkinter.ttk import *
import requests
import tkinter as tk
from tkcalendar import *
checkin = '2024-06-03'
checkout = '2024-06-16'
adult = '2'
room = '1'
children = '0'
city = ""
selected_currency = 'EUR'

def get_price(price):
    global selected_currency
    if(selected_currency=='TRY'):
        return price*30
    else:
        return price/30

def on_dropdown_select(event):
    global city
    if event != city:
        city = event

def update_table():
    for row in table.get_children():
        table.item(row, values=(table.item(row)["values"][0], table.item(row)["values"][1], table.item(row)["values"][2], table.item(row)["values"][3], get_price(float(table.item(row)["values"][4])), selected_currency))

def on_currency_select():
    global selected_currency
    if v.get() != selected_currency:
        selected_currency = v.get()
        update_table()

def sort_by_price(hotel):
    return hotel["price"]

def scrape_hotels(city,checkin,checkout,adult,children,room):
    # URL of Booking.com search results for the specified city
    url = 'https://www.booking.com/searchresults.tr.html?ss=' + city + '&ssne=' + city + '&ssne_untouched=' + city + '&label=gen173nr-1FCAEoggI46AdIM1gEaOQBiAEBmAExuAEHyAEP2AEB6AEBAECiAIBqAIDuAKo8sKxBsACAdICJGZlZWVmNGJjLWI2OGEtNGM0OS05ODk0LTM2ZGQ4YzkxYzY0MNgCBeACAQ&aid=304142&lang=tr&sb=1&src_elem=sb&src=index&dest_type=city&checkin=' + checkin + '&checkout=' + checkout + '&group_adults=' + adult + '&no_rooms=' + room + '&group_children=' + children + '&selected_currency=EUR'
    print(url)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, likeGecko) Chrome / 51.0.2704.64Safari / 537.36','Accept-Language': 'en-US, en;q=0.5'}
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find hotel elements
        hotel_elements = soup.findAll('div', {'data-testid': 'property-card'})


        # Store hotel information
        hotels = []

        # Iterate over hotel elements
        for hotel in hotel_elements[:10]:  # Limit to the first 10 hotels
            # Extract hotel attributes
            title_element = hotel.find('div', {'data-testid': 'title'})
            title = title_element.text.strip() if title_element else 'NOT GIVEN'
            address_element = hotel.find('span', {'data-testid': 'address'})
            address = address_element.text.strip() if address_element else 'NOT GIVEN'
            distance_element = hotel.find('span', {'data-testid': 'distance'})
            distance = distance_element.text.strip() if distance_element else 'NOT GIVEN'
            rating_element = hotel.find('span', {'class': 'a3332d346a'})
            rating = rating_element.text.strip() if rating_element else 'NOT GIVEN'
            price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
            price = 0
            currency = ''
            if price_element:
                price_text = price_element.text.strip().split('\xa0')
                price = float(price_text[1].replace('.', '').replace(',', '.'))
                currency = price_text[0]
            else:
                price = 0
                currency = 'NOT GIVEN'


            # Append hotel information to the list
            hotels.append({
                'title': title,
                'address': address,
                'distance_to_city_center': distance,
                'rating': rating,
                'price': price,
                'currency': currency
            })
        return sorted(hotels, key=lambda hotel: hotel['price'])
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
        return None

def get_hotels():
    global selected_currency
    if(city != '' and checkin != '' and checkout != '' and adult != '' and children != '' and room != ''):
        v.set('EUR')
        selected_currency = 'EUR'
        table.delete(*table.get_children())
        hotels = scrape_hotels(city, checkin, checkout, adult, children, room)
        if hotels:
            for hotel in hotels:
                print(hotel)
        for i in range(5):
            item = hotels[i]
            table.insert("", tk.END, values=(item["title"], item["address"], item["distance_to_city_center"], item["rating"], item['price'], item['currency']))

window = tk.Tk()
window.title("Booking.com")
window.geometry("1500x900")

options = ["Paris", "London", "Rome"]

selected_option = tk.StringVar()
dropdown = tk.OptionMenu(window, selected_option, *options, command=on_dropdown_select)
dropdown.config()

v = StringVar(window, 'EUR')
radio_EUR = tk.Radiobutton(window, text = 'EUR', variable = v,value = 'EUR', command=on_currency_select)
radio_TRY = tk.Radiobutton(window, text = 'TRY', variable = v,value = 'TRY', command=on_currency_select)

cki_label = Label(window, text='check-in-date :')
cki_label.place(x=40, y=40, width=100)

button = tk.Button(window, text="Get Hotels", command=get_hotels)
button.place(x=500, y=40)
table = Treeview(window, columns=("title", "address", "distance", "rating", "price", "currency"), show="headings")

# Define column headings and properties
#table.heading("#0", text="ID", anchor=tk.CENTER)  # Add an ID column
#table.column("#0", width=10, anchor=tk.CENTER)

table.heading("title", text="Hotel Name")
table.column("title", width=200)

table.heading("address", text="Address")
table.column("address", width=200)

table.heading("distance", text="Distance")
table.column("distance", width=120)

table.heading("rating", text="Rating")
table.column("rating", width=80)

table.heading("price", text="Price")
table.column("price", width=100, anchor=tk.CENTER)

table.heading("currency", text="Currency")
table.column("currency", width=60, anchor=tk.CENTER)

scrollbar = Scrollbar(window, orient=tk.VERTICAL, command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

table.place(x=50, y=80)

dropdown.place(x=235, y=0)
radio_EUR.place(x=400, y=30)
radio_TRY.place(x=400, y=50)


window.mainloop()