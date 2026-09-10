package com.personalshopper.app.service;

import com.personalshopper.app.model.Category;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.InputStream;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

@Service
public class ExcelImportService {
    public List<Category> loadCategories(Path excelPath) throws IOException {
        List<Category> categories = new ArrayList<>();
        try (InputStream input = Files.newInputStream(excelPath); Workbook workbook = new XSSFWorkbook(input)) {
            var sheet = workbook.getSheet("CONFIGURACIÓN");
            if (sheet == null) {
                throw new IllegalArgumentException("El Excel no contiene la hoja CONFIGURACIÓN.");
            }
            for (Row row : sheet) {
                if (row.getRowNum() == 0 || row.getCell(0) == null) {
                    continue;
                }
                categories.add(new Category(
                        row.getCell(0).getStringCellValue().trim(),
                        BigDecimal.valueOf(row.getCell(1).getNumericCellValue()),
                        BigDecimal.valueOf(row.getCell(2).getNumericCellValue())));
            }
        }
        return categories;
    }
}
