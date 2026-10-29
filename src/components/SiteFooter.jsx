import { Link } from "react-router-dom";
import {
  FaFacebookF,
  FaInstagram,
  FaLinkedinIn,
  FaYoutube,
} from "react-icons/fa6";

export default function SiteFooter() {
  return (
    <footer>
      <div className="footer-grid">
        <div className="footer-brand">
          <Link className="wordmark" to="/">
            Dr. Yogitha's
          </Link>
          <p>
            Ayurvedic hair oil inspired by botanical traditions.
            <br />A mindful ritual for your hair.
          </p>
          <div className="footer-socials" aria-label="Social media">
            <span aria-label="Facebook profile coming soon" title="Facebook">
              <FaFacebookF aria-hidden="true" />
            </span>
            <span aria-label="Instagram profile coming soon" title="Instagram">
              <FaInstagram aria-hidden="true" />
            </span>
            <span aria-label="YouTube channel coming soon" title="YouTube">
              <FaYoutube aria-hidden="true" />
            </span>
            <span aria-label="LinkedIn page coming soon" title="LinkedIn">
              <FaLinkedinIn aria-hidden="true" />
            </span>
          </div>
        </div>
        <div>
          <h3>PAGES</h3>
          <Link to="/about">About</Link>
          <Link to="/#shop">Product</Link>
          <Link to="/blog">Blog</Link>
          <Link to="/contact">Contact</Link>
        </div>
        <div>
          <h3>DISCOVER</h3>
          <Link to="/#formula">The ingredients</Link>
          <Link to="/#craft">The making</Link>
          <Link to="/#routine">Your hair ritual</Link>
        </div>
        <div className="footer-contact">
          <h3>CONTACT</h3>
          <a href="tel:+910000000000">+91 00000 00000</a>
          <a href="mailto:hello@dryogithas.example">
            hello@dryogithas.example
          </a>
          <p>123 Botanical Lane, Chennai, Tamil Nadu 600001</p>
        </div>
      </div>
      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} Dr. Yogitha's</span>
        <span>Ayurvedic Hair Oil</span>
        <Link to="/#top">Back to top ↑</Link>
      </div>
    </footer>
  );
}
