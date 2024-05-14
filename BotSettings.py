settings = {
    "DRIVER": r"C:\Users\lbcme\OneDrive\Desktop\chromedriver-win64\chromedriver.exe",
    "SKIPSIGNIN": False
}

xPaths = {
    "addToCart": '//*[@id="ProductBuy"]/div/div[2]/button',
    "noThanks": '//*[@id="modal-intermediary"]/div/div/div[2]/div[2]/button[2]',
    "signIn": "//*[@id='app']/header/div[1]/div[1]/div[2]/div[4]/a",
    "welcomeText": "//*[@id='app']/header/div[1]/div[1]/div[2]/div[4]/a/div[1]",
    "proceedToCheckout": '//*[@id="modal-intermediary"]/div/div/div[2]/div[2]/button[2]',
    "addAddressButton": '//*[@id="shippingItemCell"]/div/div[2]/div[2]/div/div[2]/div[2]/button',
    "reviewOrderButton": '//*[@id="paymentItemCell"]/div/div[3]/button[2]',
    "placeOrderButton": '//*[@id="btnCreditCard"]',
    "SubOffButton": '//*[@id="app"]/div/section/div/div/form/div[2]/div[3]/div[1]/div/div[4]/ul/li[2]/label/span',
    "saveAddressButton": '//*[@id="app"]/div/div/div/div/div[3]/button[2]',
    "fullName": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[1]/input',
    "phone": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[5]/input',
    "address": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[7]/label[2]/input',
    "city": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[11]/label[2]/input',
    "state": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[12]/label[2]/select',
    "zip": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[13]/input',
    "profileName": '//*[@id="app"]/div/div/div/div/div[2]/form/div[2]/div[15]/div[1]/input',
    "newCVVInput": '//*[@id="app"]/div/section/div/div/div/div[1]/div/div[3]/div/div[2]/div/div/div/div[2]/div[1]/div/div/label/div/div[4]/input',
    "continueToDeliveryButton": '//*[@id="app"]/div/section/div/div/div/div[1]/div/div[3]/div/div[3]/a',
    "continueToPaymentButton": '//*[@id="deliveryItemCell"]/div/div[3]/button[2]',
    "finalPlaceOrderButton": '//*[@id="Summary_Side"]/div[1]/div[2]/button',
    "summaryPlaceOrderButton": '//*[@id="Summary_Side"]/div[1]/div[1]/button'
}