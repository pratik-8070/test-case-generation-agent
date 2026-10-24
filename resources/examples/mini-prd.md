# PRD: ShopEase Engagement Release (v2.4)

## 1. Overview
This release adds three features to increase repeat purchases: Wishlist, Product Reviews and Coupon Codes at checkout.

### 1.1 Users
- Customer: a logged-in shopper.
- Guest: a shopper who is not logged in.

### 1.2 Out of scope
- Sharing wishlists with other users.
- Review moderation tooling for admins (handled by a separate release).

## 2. Wishlist
- FR-2.1 A customer can add a product to their wishlist from the product page using the heart icon. Clicking the filled heart removes it.
- FR-2.2 A wishlist can hold a maximum of 50 products. Adding a 51st shows "Your wishlist is full (50 items)".
- FR-2.3 Guests who click the heart icon are redirected to the login page and, after logging in, the product is added to their wishlist.
- FR-2.4 The wishlist page lists products with their current price and stock status, and lets the customer move an item to the cart.

## 3. Product Reviews
- FR-3.1 Only customers who have a delivered order containing the product can submit a review for it.
- FR-3.2 A review has a star rating (1–5, required) and an optional text of up to 1000 characters.
- FR-3.3 A customer can submit only one review per product; they can edit it afterwards.
- FR-3.4 The product page shows the average rating rounded to one decimal place and the total number of reviews.

## 4. Coupon Codes
- FR-4.1 A customer can enter one coupon code at checkout. Codes are case-insensitive.
- FR-4.2 A valid coupon applies its discount (percentage or fixed amount) to the order subtotal before shipping.
- FR-4.3 Each coupon has an expiry date and a minimum order subtotal. Expired coupons show "This coupon has expired"; if the subtotal is below the minimum, show "Add ₹<amount> more to use this coupon".
- FR-4.4 The discount can never make the order subtotal negative.

## 5. Non-functional
- The wishlist page should load quickly.
