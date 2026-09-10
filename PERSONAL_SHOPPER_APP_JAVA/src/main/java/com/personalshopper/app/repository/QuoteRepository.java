package com.personalshopper.app.repository;

import com.personalshopper.app.model.QuoteItem;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.jdbc.support.KeyHolder;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.sql.Statement;
import java.util.List;

@Repository
public class QuoteRepository {
    private final JdbcTemplate jdbcTemplate;

    public QuoteRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public long save(BigDecimal trm, List<QuoteItem> items) {
        BigDecimal totalCost = items.stream().map(QuoteItem::costCop).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal totalPrice = items.stream().map(QuoteItem::customerPriceCop).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal totalProfit = items.stream().map(QuoteItem::profitCop).reduce(BigDecimal.ZERO, BigDecimal::add);

        KeyHolder keyHolder = new GeneratedKeyHolder();
        jdbcTemplate.update(connection -> {
            var statement = connection.prepareStatement(
                    "INSERT INTO quotes (trm, total_cost_cop, total_price_cop, total_profit_cop) VALUES (?, ?, ?, ?)",
                    Statement.RETURN_GENERATED_KEYS);
            statement.setBigDecimal(1, trm);
            statement.setBigDecimal(2, totalCost);
            statement.setBigDecimal(3, totalPrice);
            statement.setBigDecimal(4, totalProfit);
            return statement;
        }, keyHolder);

        long quoteId = keyHolder.getKey().longValue();
        items.forEach(item -> jdbcTemplate.update(
                "INSERT INTO quote_items (quote_id, product, category, price_usd, tax_usd, total_usd, "
                        + "cost_cop, customer_price_cop, profit_cop, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                quoteId, item.product(), item.category(), item.priceUsd(), item.taxUsd(), item.totalUsd(),
                item.costCop(), item.customerPriceCop(), item.profitCop(), item.status()));
        return quoteId;
    }
}
