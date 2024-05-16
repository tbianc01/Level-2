from robocorp.tasks import task
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Browser.Selenium import Selenium
import time
import zipfile
from robocorp.tasks import task



@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.

    """



    #variables
    url = "https://robotsparebinindustries.com/#/robot-order"
    CSV_URL = "https://robotsparebinindustries.com/orders.csv"
    browser = Selenium()

    

    #call to functions
    table = get_orders(CSV_URL) #get the CSV file
    open_robot_order_website(url, browser) #open the website
    
    
    

    for row in table:

        close_annoying_modal(browser)
        fill_the_form(row, browser)
        pdfPath = store_receipt_as_pdf(str(row["Order number"]), browser)
        archive_receipts(pdfPath)
 


        




def open_robot_order_website(url, browser):
    browser.open_available_browser(url,browser_selection='chrome',maximized=True, alias="tomy")


def get_orders(url):

    http = HTTP()
    http.download(url= url, overwrite=True)
    
    table = Tables()
    data = table.read_table_from_csv("orders.csv", header = True)
    
    return data
    

def close_annoying_modal(browser):
    browser.switch_browser("tomy")
    browser.click_button("OK")
   

def fill_the_form(row, browser: Selenium):

    valueHead = str(row["Head"]) #value of the head of CSV
    


    browser.switch_browser("tomy")



    browser.select_from_list_by_value("id:head",valueHead)
    browser.select_radio_button("body", str(row["Body"]))
    time.sleep(0.4)
    browser.input_text("//input[@placeholder='Enter the part number for the legs']", str(row["Legs"]))
    time.sleep(0.4)
    browser.input_text("//input[@placeholder='Shipping address']",str(row["Address"]))
    time.sleep(0.7)
    browser.scroll_element_into_view("//button[@id='order']")
    time.sleep(0.4)
    browser.click_button("//button[@id='order']")
   

    time.sleep(0.8)
    while browser.does_page_contain_element("id:order"):
            
            script = "document.getElementById('order').scrollIntoView();"
            browser.execute_javascript(script)
            time.sleep(0.4)
            browser.click_button("//button[@id='order']")
    

def store_receipt_as_pdf(orderNumber, browser: Selenium):

    output_path = "output/receipts/" + orderNumber + ".pdf"

    time.sleep(0.5)
    resultHTML:Selenium = browser.get_element_attribute("//div[@id='order-completion']","innerHTML") #da error en las ultimas ejecuciones
    

    pdf = PDF()
    pdf.html_to_pdf(resultHTML,output_path)

    time.sleep(0.3)

    screenPath = screenshot_robot( orderNumber, browser)

    time.sleep(0.1)
    embed_screenshot_to_receipt(screenPath, output_path)

    time.sleep(0.1)
    browser.click_button("//button[@id='order-another']")

    return output_path

def screenshot_robot(order_number, browser: Selenium):
    output_path = "output/receipts/" + order_number + ".png"
    browser.capture_page_screenshot(output_path)
    return output_path
def embed_screenshot_to_receipt(screenshot, pdf_file):

    pdf = PDF()
    list_of_screenshots = [screenshot]

    pdf.add_files_to_pdf(files = list_of_screenshots, target_document = pdf_file, append = True)
def archive_receipts(file):
    zip_name = "Files.zip"
    files_to_add = [file]

    with zipfile.ZipFile(zip_name, "a") as myzip:
        for file in files_to_add:
            myzip.write(file, arcname= file.split('/')[-1])