import { createContext, useState, useContext } from "react";

const CategoryModalContext = createContext();

export const CategoryModalProvider = ({ children }) => {
  const [showCategoryModal, setShowCategoryModal] = useState(false);

  const openCategoryModal = () => setShowCategoryModal(true);
  const closeCategoryModal = () => setShowCategoryModal(false);

  return (
    <CategoryModalContext.Provider
      value={{ showCategoryModal, openCategoryModal, closeCategoryModal }}
    >
      {children}
    </CategoryModalContext.Provider>
  );
};

export const useCategoryModal = () => useContext(CategoryModalContext);
