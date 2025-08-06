import express from "express";
import cors from "cors";
import connectDB from "./config/db.js";
import chatRoutes from "./Routes/ChatRoutes.js";
import userRoutes from "./Routes/UserRoutes.js";
import documentRoutes from "./Routes/DocumentRoutes.js"; // ADD THIS LINE

const app = express();
const PORT = process.env.PORT || 5000;

// Connect to MongoDB
connectDB();

// Middleware to parse JSON requests
app.use(express.json());

// Middleware to handle URL-encoded data
app.use(express.urlencoded({ extended: true }));

// Middleware to handle CORS
app.use(cors());

// Middleware to serve static files
app.use(express.static("public"));

// Sample route to test the server
app.get("/", (req, res) => {
  res.send("Welcome to the PolicyPal Server!");
});

// --- API Routes ---
app.use("/api/chat", chatRoutes);
app.use("/api/user", userRoutes);
app.use("/api/documents", documentRoutes);

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
