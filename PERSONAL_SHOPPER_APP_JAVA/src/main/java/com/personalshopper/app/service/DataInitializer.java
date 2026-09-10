package com.personalshopper.app.service;

import com.personalshopper.app.repository.CategoryRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.nio.file.Path;

@Component
public class DataInitializer implements CommandLineRunner {
    private final CategoryRepository categoryRepository;
    private final ExcelImportService excelImportService;
    private final String excelPath;

    public DataInitializer(CategoryRepository categoryRepository,
                           ExcelImportService excelImportService,
                           @Value("${app.excel-path}") String excelPath) {
        this.categoryRepository = categoryRepository;
        this.excelImportService = excelImportService;
        this.excelPath = excelPath;
    }

    @Override
    public void run(String... args) throws Exception {
        if (categoryRepository.count() == 0) {
            excelImportService.loadCategories(Path.of(excelPath))
                    .forEach(categoryRepository::save);
        }
    }
}
