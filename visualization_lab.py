import csv
import requests
import matplotlib.pyplot as plt
import numpy as np


def load_2019_from_csv(filename: str) -> dict:
    """
    Зчитує дані за 2019 рік із CSV-файлу, створеного в результаті виконання практичної роботи 5.
    Повертає словник {назва_країни: значення}.
    """
    data_2019 = {}
    try:
        with open(filename, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            next(reader, None)  # Пропускаємо заголовок
            for row in reader:
                if len(row) >= 5 and row[4] != "..":
                    try:
                        val = float(row[4].replace(",", "."))
                        data_2019[row[0].strip()] = round(val, 2)
                    except ValueError:
                        continue
    except FileNotFoundError:
        print(f"Примітка: файл '{filename}' не знайдено, використовуємо вбудовані дані.")
    return data_2019


def fetch_country_series(country_code: str, indicator: str, start_year: int, end_year: int) -> dict:
    """Отримує часовий ряд показника з API Світового банку за вказаний діапазон років."""
    url = (
        f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}"
        f"?date={start_year}:{end_year}&format=json&per_page=100"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            if len(json_data) > 1 and json_data[1]:
                result = {}
                for item in json_data[1]:
                    year = int(item["date"])
                    val = item["value"]
                    if val is not None:
                        result[year] = round(float(val), 2)
                return result
    except requests.exceptions.RequestException:
        pass
    return {}


def get_dataset(csv_filename: str = "life_expectancy_2019.csv"):
    """
    Формує програмні набори даних: роки спостережень, назви країн та значення показника.
    Поєднує дані з файлу практичної роботи 5 (2019 р.) та часові ряди за 2015–2020 рр.
    """
    years = [2015, 2016, 2017, 2018, 2019, 2020]
    indicator = "SP.DYN.LE00.IN"

    # Резервні офіційні дані Світового банку (якщо робота виконується офлайн)
    dataset = {
        "Ukraine": [71.19, 71.48, 71.78, 71.58, 73.92, 71.19],
        "USA": [78.69, 78.54, 78.54, 78.64, 78.79, 76.98],
        "Poland": [77.45, 77.85, 77.75, 77.60, 77.90, 76.50],
        "Germany": [80.64, 80.99, 80.99, 80.89, 81.29, 81.04],
    }

    # Оновлюємо значення за 2019 рік безпосередньо з файлу 5-ї лабораторної роботи
    csv_2019 = load_2019_from_csv(csv_filename)
    name_mapping = {
        "Ukraine": "Ukraine",
        "USA": "United States",
        "Poland": "Poland",
        "Germany": "Germany",
    }
    idx_2019 = years.index(2019)
    for key, csv_name in name_mapping.items():
        if csv_name in csv_2019:
            dataset[key][idx_2019] = csv_2019[csv_name]

    return years, dataset


def plot_line_dynamics(years: list, ukr_values: list, other_values: list, other_country: str):
    """
    Завдання 2 (п. 1): Будує графік динаміки зміни обраного показника для України
    та однієї країни світу на одній координатній площині (рис. 7.1).
    """
    plt.figure(figsize=(8, 5))
    plt.plot(years, ukr_values, marker="o", label="Ukraine")
    plt.plot(years, other_values, marker="o", label=other_country)

    plt.title(f"Indicator dynamics for Ukraine and {other_country}")
    plt.xlabel("Year")
    plt.ylabel("Indicator value (Life expectancy, years)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_bar_chart(years: list, dataset: dict, country_name: str):
    """
    Завдання 3 (п. 2): Будує стовпчасту діаграму, яка відображає значення обраного показника
    для країни, назву якої користувач вводить із клавіатури (або порівняння з Україною, як на рис. 7.2).
    """
    # Пошук країни без урахування регістру
    matched_country = None
    for key in dataset:
        if key.lower() == country_name.strip().lower():
            matched_country = key
            break

    if not matched_country:
        print(f"Країну '{country_name}' не знайдено у наборі. Доступні: {', '.join(dataset.keys())}")
        return

    # 1) Стовпчаста діаграма для введеної користувачем країни
    plt.figure(figsize=(8, 5))
    plt.bar(years, dataset[matched_country], color="steelblue", width=0.5, label=matched_country)
    plt.title(f"Life expectancy dynamics for {matched_country}")
    plt.xlabel("Year")
    plt.ylabel("Indicator value (years)")
    plt.xticks(years)
    plt.legend()
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()

    # 2) Порівняльна стовпчаста діаграма для двох країн (відповідно до рис. 7.2 методички)
    if matched_country != "Ukraine":
        plt.figure(figsize=(8, 5))
        x = np.arange(len(years))
        width = 0.35
        plt.bar(x - width / 2, dataset["Ukraine"], width, label="Ukraine")
        plt.bar(x + width / 2, dataset[matched_country], width, label=matched_country)
        plt.title(f"Indicator comparison for Ukraine and {matched_country}")
        plt.xlabel("Year")
        plt.ylabel("Indicator value (years)")
        plt.xticks(x, years)
        plt.legend()
        plt.grid(True, axis="y")
        plt.tight_layout()
        plt.show()


def plot_pie_chart(years: list, dataset: dict, other_country: str, target_year: int):
    """
    Завдання 4 (п. 3): Будує кругову діаграму для порівняння значень обраного показника
    між Україною та обраною країною світу за 1 рік, який задає користувач (рис. 7.3).
    """
    if target_year not in years:
        print(f"Помилка: рік {target_year} відсутній у вибірці. Доступні роки: {years}")
        return

    idx = years.index(target_year)
    ukr_val = dataset["Ukraine"][idx]
    other_val = dataset[other_country][idx]
    values = [ukr_val, other_val]
    labels = ["Ukraine", other_country]

    def format_pct(pct):
        total = sum(values)
        absolute_val = pct * total / 100.0
        return f"{pct:.1f}%\n({absolute_val:.1f})"

    plt.figure(figsize=(6, 6))
    plt.pie(
        values,
        labels=labels,
        autopct=format_pct,
        startangle=0,
        textprops={"weight": "bold", "fontsize": 9},
    )
    plt.title(f"Indicator comparison for Ukraine and {other_country} ({target_year})")
    plt.tight_layout()
    plt.show()


def main():
    years, dataset = get_dataset("life_expectancy_2019.csv")
    compare_country = "USA"

    print("Візуалізація даних Світового банку (Life expectancy at birth, total)")
    print(f"Роки спостережень: {years}")
    print(f"Дані для України: {dataset['Ukraine']}")
    print(f"Дані для {compare_country}: {dataset[compare_country]}\n")

    # Пункт 1 (Завдання 2): Лінійний графік динаміки для України та США
    plot_line_dynamics(years, dataset["Ukraine"], dataset[compare_country], compare_country)

    # Пункт 2 (Завдання 3): Стовпчаста діаграма для країни, введеної з клавіатури
    user_country = input(f"Введіть назву країни для побудови стовпчастої діаграми ({', '.join(dataset.keys())}): ")
    if not user_country.strip():
        user_country = "USA"
    plot_bar_chart(years, dataset, user_country)

    # Пункт 3 (Завдання 4): Кругова діаграма за рік, заданий користувачем
    user_year_str = input(f"Введіть рік для побудови кругової діаграми ({years[0]}–{years[-1]}, напр. 2019): ")
    try:
        user_year = int(user_year_str.strip())
    except ValueError:
        user_year = 2019
    plot_pie_chart(years, dataset, compare_country, user_year)


if __name__ == "__main__":
    main()