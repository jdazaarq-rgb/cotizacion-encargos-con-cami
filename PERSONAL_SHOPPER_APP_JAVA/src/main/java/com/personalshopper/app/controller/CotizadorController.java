package com.personalshopper.app.controller;

import com.personalshopper.app.model.Category;
import com.personalshopper.app.model.QuoteItem;
import com.personalshopper.app.repository.CategoryRepository;
import com.personalshopper.app.repository.QuoteRepository;
import com.personalshopper.app.service.PricingService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.SessionAttributes;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

@Controller
@SessionAttributes("items")
public class CotizadorController {
    private final CategoryRepository categoryRepository;
    private final QuoteRepository quoteRepository;
    private final PricingService pricingService;

    public CotizadorController(CategoryRepository categoryRepository,
                               QuoteRepository quoteRepository,
                               PricingService pricingService) {
        this.categoryRepository = categoryRepository;
        this.quoteRepository = quoteRepository;
        this.pricingService = pricingService;
    }

    @ModelAttribute("items")
    public List<QuoteItem> items() {
        return new ArrayList<>();
    }

    @GetMapping("/")
    public String index(Model model, @ModelAttribute("items") List<QuoteItem> items) {
        model.addAttribute("categories", categoryRepository.findAll());
        addTotals(model, items);
        return "cotizador";
    }

    @PostMapping("/agregar")
    public String add(
            @RequestParam String product,
            @RequestParam String categoryName,
            @RequestParam BigDecimal priceUsd,
            @RequestParam BigDecimal trm,
            @ModelAttribute("items") List<QuoteItem> items,
            RedirectAttributes redirectAttributes) {
        try {
            Category category = categoryRepository.findAll().stream()
                    .filter(value -> value.name().equals(categoryName))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("Categoría no encontrada."));
            items.add(pricingService.calculate(product, category, priceUsd, trm));
        } catch (IllegalArgumentException error) {
            redirectAttributes.addFlashAttribute("error", error.getMessage());
        }
        return "redirect:/";
    }

    @PostMapping("/quitar/{index}")
    public String remove(@PathVariable int index, @ModelAttribute("items") List<QuoteItem> items) {
        if (index >= 0 && index < items.size()) {
            items.remove(index);
        }
        return "redirect:/";
    }

    @PostMapping("/guardar")
    public String save(@RequestParam BigDecimal trm,
                       @ModelAttribute("items") List<QuoteItem> items,
                       RedirectAttributes redirectAttributes) {
        if (items.isEmpty()) {
            redirectAttributes.addFlashAttribute("error", "Agrega al menos un producto.");
        } else {
            long quoteId = quoteRepository.save(trm, items);
            items.clear();
            redirectAttributes.addFlashAttribute("success", "Cotización " + quoteId + " guardada.");
        }
        return "redirect:/";
    }

    private void addTotals(Model model, List<QuoteItem> items) {
        model.addAttribute("totalCost", items.stream().map(QuoteItem::costCop).reduce(BigDecimal.ZERO, BigDecimal::add));
        model.addAttribute("totalPrice", items.stream().map(QuoteItem::customerPriceCop).reduce(BigDecimal.ZERO, BigDecimal::add));
        model.addAttribute("totalProfit", items.stream().map(QuoteItem::profitCop).reduce(BigDecimal.ZERO, BigDecimal::add));
    }
}
