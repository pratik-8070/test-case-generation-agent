Feature: Add to Cart — Acceptance Criteria

AC-CART-1
Given a product that is in stock
When the shopper clicks "Add to cart" on the product detail page
Then the product is added to the cart with quantity 1
And the cart icon count increases by 1
And the toast "Added to cart" is displayed

AC-CART-2
Given the product is already in the cart
When the shopper adds it again
Then the quantity of the existing cart line increases by 1 instead of creating a new line

AC-CART-3
Given the shopper selects a quantity on the product detail page
Then the quantity must be a whole number between 1 and 10 inclusive

AC-CART-4
Given a cart line already has quantity 10
When the shopper tries to add the same product again
Then the message "You can buy a maximum of 10 units of this item" is displayed and the quantity stays at 10

AC-CART-5
Given the requested quantity exceeds available stock
When the shopper clicks "Add to cart"
Then the message "Only <n> left in stock" is displayed and nothing is added

AC-CART-6
Given a guest (not logged in) shopper
When they add a product to the cart
Then the item is stored in a guest cart and is merged into their account cart when they log in
