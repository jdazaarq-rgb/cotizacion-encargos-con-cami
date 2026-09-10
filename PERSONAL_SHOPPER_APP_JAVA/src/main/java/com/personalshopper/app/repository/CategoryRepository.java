package com.personalshopper.app.repository;

import com.personalshopper.app.model.Category;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class CategoryRepository {
    private final JdbcTemplate jdbcTemplate;

    public CategoryRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public long count() {
        return jdbcTemplate.queryForObject("SELECT COUNT(*) FROM categories", Long.class);
    }

    public void save(Category category) {
        jdbcTemplate.update(
                "INSERT INTO categories (name, surcharge_rate, minimum_profit) VALUES (?, ?, ?)",
                category.name(), category.surchargeRate(), category.minimumProfit());
    }

    public List<Category> findAll() {
        return jdbcTemplate.query(
                "SELECT name, surcharge_rate, minimum_profit FROM categories WHERE active = 1 ORDER BY id",
                (result, rowNumber) -> new Category(
                        result.getString("name"),
                        result.getBigDecimal("surcharge_rate"),
                        result.getBigDecimal("minimum_profit")));
    }
}
