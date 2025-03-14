from playwright.sync_api import sync_playwright, expect
import logging
from counciladaptors.counciladaptor import CouncilAdaptor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SouthRibbleAdaptor(CouncilAdaptor):

    def __init__(self):
        super().__init__("South Ribble", "Lancashire", "England", {'Household Waste Non-Recyclable Waste': 'Black', 'Garden Waste Collection': 'Brown', 'Blue/Green Recyclable Waste': 'Blue'})

    def extract_bin_dates(self, door_number, postcode):
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto("https://southribble.gov.uk/bincollectiondays", timeout=0)
                logging.debug("Navigating to https://southribble.gov.uk/bincollectiondays")

                page.get_by_role("link", name="Check your collection day").click()
                expect(page).to_have_title("What are my waste collections date - My South Ribble")

                page.get_by_role("button", name="Close").click()
                page.get_by_role("button", name="Continue").click()

                frame = page.frame_locator("iframe[title=\"What are my waste collections date\"]").first
                frame.get_by_role("textbox", name="Postcode / street search (min").click()
                frame.get_by_role("textbox", name="Postcode / street search (min").fill(postcode)
                page.wait_for_timeout(3000)
                frame.get_by_role("link", name="Select...").click()

                frame.get_by_role("option", name=door_number).click()
                frame.get_by_role("button", name="Next ").click()
                logging.debug("Calendar loaded")

                page.wait_for_timeout(5000)

                # Return the table below as map of Type and Date
                waste_collection_map = {}
                waste_collections = frame.locator("tbody#WasteCollections tr")

                for row in waste_collections.all():
                    cells = row.locator("td")
                    if cells.count() == 3:
                        waste_type = self.clean_string(cells.nth(1).inner_text().strip())
                        collection_date = cells.nth(2).locator("h5").inner_text().strip(", ").strip()

                        collection_date = self.format_date(collection_date)
                        waste_collection_map["{} ({})".format(waste_type, self.assign_colour(waste_type))] = collection_date

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                waste_collection_map = {}

            finally:
                browser.close()

            return waste_collection_map

            browser.close()

            return waste_collection_map
