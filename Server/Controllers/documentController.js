import axios from "axios";
import FormData from "form-data";

const ML_API_URL = "http://localhost:8000/api/process";

export const processDocument = async (req, res) => {
  try {
    // Destructure file and query from the request object for cleaner code
    const { file } = req;
    const { query } = req.body;

    // Now we can use 'file' and 'query' directly
    if (!file || !query) {
      return res
        .status(400)
        .json({ message: "A PDF file and a query string are required." });
    }

    // Your debugging logs will now work correctly
    console.log("--- Received File ---");
    console.log(file.originalname);
    console.log("--- Received Query ---");
    console.log(query);

    console.log(
      "[Node.js] Received request. Calling Python ML service (this may take a while)..."
    );

    const formData = new FormData();
    console.log(formData);
    formData.append("file", file.buffer, { filename: file.originalname });
    formData.append("query", query); // Use the 'query' constant
    console.log(formData);
    const mlResponse = await axios.post(ML_API_URL, formData, {
      headers: {
        ...formData.getHeaders(),
      },
      timeout: 300000,
    });
    console.log(mlResponse);
    console.log("[Node.js] Success! Received JSON response from Python.");
    res.status(200).json(mlResponse.data);
  } catch (error) {
    console.error("[Node.js] Error contacting ML service:", error.message);
    if (error.response) {
      res.status(error.response.status).json({
        message: error.response.data.detail || "Error from ML service.",
      });
    } else {
      res.status(500).json({
        message:
          "Could not connect to the ML processing service or the request timed out.",
      });
    }
  }
};
