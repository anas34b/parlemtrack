import type { Metadata, Viewport } from "next";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import EnregistrerServiceWorker from "@/components/EnregistrerServiceWorker";
import "./globals.css";

export const metadata: Metadata = {
  title: "ParlemTrack",
  description: "Les votes de l'Assemblée nationale, expliqués simplement.",
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "ParlemTrack",
  },
};

export const viewport: Viewport = {
  themeColor: "#18181b",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
        <EnregistrerServiceWorker />
        <a href="#contenu-principal" className="lien-evitement">
          Aller au contenu principal
        </a>
        <Header />
        <main id="contenu-principal" className="conteneur" style={{ flex: 1, width: "100%", padding: "24px 20px 64px" }}>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
