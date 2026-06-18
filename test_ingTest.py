import pytest
from multiprocessing import Process
from playwright.sync_api import sync_playwright
import os

# ta funkcja wykona się w osobnym procesie dla każdej przeglądarki
def wykonaj_test_na_przegladarce(nazwa_przegladarki):
    print(nazwa_przegladarki.upper())

    with sync_playwright() as p:
        browser_type = getattr(p, nazwa_przegladarki)
        if "CI" in os.environ:
            browser = browser_type.launch(headless=True)    # dla pipeline musi być headless
        else:
            browser = browser_type.launch(headless=False, slow_mo=1500) # headless=False żeby odpalić przeglądarki
                                                                        # slowmo żeby widzieć kroki
        page = browser.new_page()
    
        page.goto("https://ing.pl")     # odpalamy strone ing.pl
        page.get_by_role('button', name='Dostosuj').click()   # klikamy w button z name Dostosuj
        page.locator('[name="CpmAnalyticalOption"]').click()  # klikamy w button z unikalnym name CpmAnalyticalOption
        page.get_by_role('button', name='Zaakceptuj zaznaczone').click()  # klikamy w button z name Zaakceptuj zaznaczone
    
        cookies = page.context.cookies()    # wyciągamy i printujemy cookiesy
        print(f"\n--- COOKIES FOR {nazwa_przegladarki.upper()} ---")
        for cookie in cookies:
            print(f"[{nazwa_przegladarki.upper()}] {cookie['name']}: {cookie['value']}")

        browser.close()

# główna funkcja testowa, którą uruchomi Pytest
def test_uruchom_wszystkie_jednoczesnie():
    przegladarki = ["chromium", "firefox", "webkit"]
    procesy = []

    # tworzymy osobny proces systemowy dla każdej przeglądarki
    for b in przegladarki:
        p = Process(target=wykonaj_test_na_przegladarce, args=(b,))
        procesy.append(p)
        p.start() # Uruchamia proces

    # czekamy, aż wszystkie procesy zakończą swoją pracę
    for p in procesy:
        p.join()