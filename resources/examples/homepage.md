# Homepage

The homepage is the landing page of the ShopEase web store at `/`. It is shown to both guests and logged-in customers.

At the top there is a header with the ShopEase logo (clicking it always returns to the homepage), a search bar, a cart icon showing the number of items in the cart, and a "Sign in" link. When the customer is logged in, the "Sign in" link is replaced by "Hi, <first name>".

Below the header is a hero banner carousel that rotates through up to 5 promotional banners every 6 seconds. Customers can move between banners using left/right arrows, and each banner links to its promotion page. If there are no active promotions, the carousel is hidden.

Next is a "Featured Products" grid showing 8 products. Each product card displays the product image, name, price and an "Add to cart" button. Out-of-stock products show an "Out of stock" label instead of the button.

The search bar requires at least 2 characters; pressing Enter or clicking the search icon opens the results page at `/search?q=<term>`.

The footer contains links to About Us, Contact, Privacy Policy and Terms of Service.

The page must be usable on mobile (≤ 480px wide), where the featured grid shows 2 products per row instead of 4.
