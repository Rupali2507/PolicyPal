import express from "express";
import multer from "multer";
import { processDocument } from "../Controllers/documentController.js";

const router = express.Router();

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

router.post("/process", upload.single("file"), processDocument);

export default router;
