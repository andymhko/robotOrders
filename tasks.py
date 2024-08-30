from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive

@task
def robot_order_python():
    browser.configure(slowmo=100,)
    open_robot_order_website()
    close_annoying_modal()
    get_orders()
    archive_receipts()

def open_robot_order_website():
    """navigate to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Choose to give up your constitutional rights"""
    page = browser.page()
    page.click("button:text('I guess so...')")

def get_orders():
    """get othe orders csv file"""
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True)
    table = Tables()
    rows = table.read_table_from_csv("orders.csv",header=True)
    for row in rows:
        fill_the_form(row)

def fill_the_form(robotOrder):
    """configure and order the robot"""
    page = browser.page()
    #page.select_option("#head","D.A.V.E head")
    page.select_option("#head",robotOrder["Head"])
    match robotOrder["Body"]:
        case "1":
            page.check("#id-body-1")
        case "2":
            page.check("#id-body-2")
        case "3":
            page.check("#id-body-3")
        case "4":
            page.check("#id-body-4")
        case "5":
            page.check("#id-body-5")
        case "6":
            page.check("#id-body-6")
    #page.get_by_placeholder("Enter the part number for the legs").fill("3")
    page.get_by_placeholder("Enter the part number for the legs").fill(robotOrder["Legs"])
    page.fill("#address",robotOrder["Address"])
    preview_robot()
    submit_order()
    store_receipt_as_pdf(robotOrder["Order number"])
    screenshot_robot(robotOrder["Order number"])
    currentReceipt = "output/receipt" + str(robotOrder["Order number"]) + ".pdf"
    currentScreenshot="output/robot" + str(robotOrder["Order number"]) + ".png"
    list_of_files = [currentScreenshot]
    embed_screenshot_to_receipt(list_of_files,currentReceipt)
    page.click("button:text('ORDER ANOTHER ROBOT')")
    close_annoying_modal()
    #embed_screenshot_to_receipt("output/screenshot"+robotOrder,pdf_file)
    
def preview_robot():
    """click preview to see the robot before ordering"""
    page = browser.page()
    page.click("button:text('Preview')")

def submit_order():
    page = browser.page()
    page.click("button:text('ORDER')")
    while page.content().find("alert alert-danger") >= 0:
        page.click("button:text('ORDER')")
    # if page.content().find("alert alert-danger") >= 0:
    #     page.click("button:text('ORDER')")
    # else:
    #     pass
        
def screenshot_robot(order_number):
    """take a screenshot of the receipt"""
    page = browser.page()
    screenshotname = "output/robot" + str(order_number) + ".png"
    page.screenshot(path=screenshotname)

def embed_screenshot_to_receipt(filesList,receipt):
    """add the screenshot to the pdf file"""
    pdf = PDF()
    pdf.add_files_to_pdf(filesList,receipt,True)

def store_receipt_as_pdf(order_number):
    """export receipt to pdf"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    outputlocation = "output/receipt" + str(order_number) + ".pdf"
    pdf.html_to_pdf(receipt_html,outputlocation)

def archive_receipts():
    """zip the PDF receipts into one file"""
    archive = Archive()
    archive.archive_folder_with_zip("output","output\zippedReceipts.zip",False,"*.pdf","stored")