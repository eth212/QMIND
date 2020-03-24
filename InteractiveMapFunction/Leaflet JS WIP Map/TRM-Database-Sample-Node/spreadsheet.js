// Function for getting in database values through GoogleSpreadsheet API

const { GoogleSpreadsheet } = require("google-spreadsheet");
const creds = require("./client_secret.json");

// Colab File - spreadsheet key is the long id in the sheets URL -
const doc = new GoogleSpreadsheet(
  "1QQrVIIhGDfW4BNFO0XBwUOLC2GfpNiNtZDglWfc_hkk"
);

async function accessSpreadsheet() {
  await doc.useServiceAccountAuth({
    client_email: creds.client_email,
    private_key: creds.private_key
  });

  await doc.loadInfo(); // loads document properties and worksheets
  console.log(doc.title);

  const sheet = doc.sheetsByIndex[0]; // or use doc.sheetsById[id]
  console.log(sheet.title);
  console.log(sheet.rowCount);

  //Takes awhile to buffer and read in all rows
  const rows = await sheet.getRows(); // can pass in { limit, offset }

  console.log(
    rows[400].Year + " , make " + rows[400].Make + " L " + rows[400].Location
  );
  // read/write row values
  for (let i = 0; i < 100; i++) {
    console.log(
      "i is:  " +
        i +
        " Year: " +
        rows[i].SaleDate +
        " , make: " +
        rows[i].Make +
        ", L: " +
        rows[i].Location
    );
  }
}

accessSpreadsheet();
