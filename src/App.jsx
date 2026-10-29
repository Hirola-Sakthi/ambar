import { useEffect, useRef, useState } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import AboutPage from "./pages/AboutPage";
import BlogPage from "./pages/BlogPage";
import ContactPage from "./pages/ContactPage";
import HomePage from "./pages/HomePage";
import BagDialog from "./components/BagDialog";
import SiteFooter from "./components/SiteFooter";
import SiteHeader from "./components/SiteHeader";

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const lenisRef = useRef(null);
  const dialog = useRef(null);
  const location = useLocation();
  const [bagQuantity, setBagQuantity] = useState(() => {
    const quantity = Number(localStorage.getItem("yogitha-hair-oil-bag"));
    return Number.isSafeInteger(quantity) && quantity > 0 ? quantity : 0;
  });

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const lenis = new Lenis({
      lerp: 0.12,
      smoothWheel: true,
      syncTouch: false,
    });
    lenisRef.current = lenis;
    lenis.on("scroll", ScrollTrigger.update);
    const tick = (time) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    return () => {
      gsap.ticker.remove(tick);
      lenis.destroy();
      lenisRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (location.hash) {
      const target = document.getElementById(location.hash.slice(1));
      if (!target) return;
      if (lenisRef.current) {
        lenisRef.current.scrollTo(target, {
          duration: 1.1,
          onComplete: () => target.focus({ preventScroll: true }),
        });
      } else {
        target.scrollIntoView();
        target.focus({ preventScroll: true });
      }
      return;
    }

    lenisRef.current?.scrollTo(0, { immediate: true });
    window.scrollTo(0, 0);
  }, [location.key, location.pathname, location.hash]);

  const navigate = (event) => {
    const href = event.target.closest("a")?.getAttribute("href");
    if (
      !href?.startsWith("#") ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const target = document.getElementById(href.slice(1));
    if (!target) return;
    event.preventDefault();
    const complete = () => {
      history.replaceState(history.state, "", href);
      target.focus({ preventScroll: true });
    };
    if (lenisRef.current)
      lenisRef.current.scrollTo(target, {
        duration: 1.1,
        onComplete: complete,
      });
    else {
      target.scrollIntoView();
      complete();
    }
  };

  const openCart = () => {
    dialog.current.showModal();
    lenisRef.current?.stop();
  };
  const updateBagQuantity = (quantity) => {
    const next = Math.max(0, quantity);
    localStorage.setItem("yogitha-hair-oil-bag", String(next));
    setBagQuantity(next);
  };

  return (
    <div onClick={navigate}>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <SiteHeader bagQuantity={bagQuantity} openCart={openCart} />
      <main id="main-content" tabIndex={-1}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route
            path="*"
            element={
              <section className="info-page coming-soon-page">
                <div className="info-page-inner">
                  <p className="eyebrow">PAGE NOT FOUND</p>
                  <h1>We couldn't find that page.</h1>
                  <p className="info-page-lead">
                    The page may have moved. Return home to explore Dr.
                    Yogitha's Ayurvedic hair oil.
                  </p>
                  <a className="pill-button info-page-button" href="/">
                    Return home <span aria-hidden="true">↗</span>
                  </a>
                </div>
              </section>
            }
          />
        </Routes>
      </main>
      <SiteFooter />
      <BagDialog
        ref={dialog}
        bagQuantity={bagQuantity}
        lenisRef={lenisRef}
        updateBagQuantity={updateBagQuantity}
      />
    </div>
  );
}
