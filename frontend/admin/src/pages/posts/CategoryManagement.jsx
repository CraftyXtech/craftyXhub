import React, { useState, useMemo } from "react";
import { Modal, ModalHeader, ModalBody, ModalFooter, Row, Col, Button, Card, Alert } from "reactstrap";
import { useForm } from "react-hook-form";
import Head from "@/layout/head/Head";
import Content from "@/layout/content/Content";
import {
  Block,
  BlockHead,
  BlockTitle,
  BlockBetween,
  BlockHeadContent,
  BlockDes,
  Icon,
  DataTableHead,
  DataTableBody,
  DataTableRow,
  DataTableItem,
  PaginationComponent,
  BackTo,
} from "@/components/Component";
import { useGetCategories, useCreateCategory, useUpdateCategory, useDeleteCategory } from "@/api/postService";
import { toast } from "react-toastify";

const CategoryManagement = () => {
  const { register, handleSubmit, reset, formState: { errors }, watch, setValue } = useForm();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage, setItemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [modalMode, setModalMode] = useState("create"); // "create" or "edit"
  const [sm, updateSm] = useState(false);
  const [expandedParents, setExpandedParents] = useState(new Set());

  // API hooks
  const { categories, loading, error, refetch } = useGetCategories();
  const { createCategory, loading: createLoading } = useCreateCategory();
  const { updateCategory, loading: updateLoading } = useUpdateCategory();
  const { deleteCategory, loading: deleteLoading } = useDeleteCategory();

  const watchedParentId = watch("parent_id");



  const flattenCategories = (cats) => {
    const flattened = [];
    cats.forEach(category => {
      flattened.push({ 
        ...category, 
        level: 0, 
        isParent: !category.parent_id,
        type: "parent",
        hasSubcategories: category.subcategories && category.subcategories.length > 0
      });
      if (category.subcategories && category.subcategories.length > 0) {
        category.subcategories.forEach(subcat => {
          flattened.push({ 
            ...subcat, 
            level: 1, 
            isParent: false, 
            parent_name: category.name,
            parent_id: category.id,
            type: "subcategory"
          });
        });
      }
    });
    return flattened;
  };
  const flatCategories = useMemo(() => flattenCategories(categories), [categories]);
  
  // Filter categories based on search
  const filteredCategories = useMemo(() => {
    const q = searchText.trim().toLowerCase();
    if (!q) return flatCategories;
    return flatCategories.filter(category =>
      category.name.toLowerCase().includes(q) ||
      category.slug.toLowerCase().includes(q) ||
      (category.parent_name && category.parent_name.toLowerCase().includes(q))
    );
  }, [flatCategories, searchText]);

  // Visible list respects expansion state. When searching, always show matches regardless of expansion.
  const visibleCategories = useMemo(() => {
    const q = searchText.trim();
    const results = [];
    for (const cat of filteredCategories) {
      if (cat.type === "subcategory" && !q) {
        if (expandedParents.has(cat.parent_id)) results.push(cat);
      } else {
        results.push(cat);
      }
    }
    return results;
  }, [filteredCategories, expandedParents, searchText]);


  const indexOfLastItem = currentPage * itemPerPage;
  const indexOfFirstItem = indexOfLastItem - itemPerPage;
  const currentItems = visibleCategories.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(visibleCategories.length / itemPerPage);


  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  };

  const getAvailableParentCategories = (excludeId = null) => {
    return categories.filter(cat => 
      !cat.parent_id && 
      cat.id !== excludeId 
    );
  };

  const onFilterChange = (e) => {
    setSearchText(e.target.value);
    setCurrentPage(1);
  };

  const toggleExpand = (parentId) => {
    setExpandedParents(prev => {
      const next = new Set(prev);
      if (next.has(parentId)) next.delete(parentId); else next.add(parentId);
      return next;
    });
  };

  const onCreateSubmit = async (data) => {
    try {
      if (data.parent_id && data.parent_id !== "") {
        const parentCategory = categories.find(cat => cat.id === parseInt(data.parent_id));
        if (!parentCategory) {
          toast.error("Selected parent category not found");
          return;
        }
        
        if (parentCategory.subcategories && parentCategory.subcategories.length >= 10) {
          toast.warning("Parent category already has maximum number of subcategories");
          return;
        }
      }

      const categoryData = {
        ...data,
        slug: generateSlug(data.name),
        parent_id: data.parent_id && data.parent_id !== "" ? parseInt(data.parent_id) : null
      };
      
      await createCategory(categoryData);
      toast.success(`Category "${data.name}" created successfully`);
      setShowModal(false);
      reset();
      refetch();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Failed to create category";
      toast.error(errorMessage);
    }
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingCategory(null);
    setModalMode("create");
    reset();
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setModalMode("edit");
    reset({
      name: category.name,
      description: category.description || '',
      parent_id: category.parent_id || ''
    });
    setShowModal(true);
  };

  const onUpdateSubmit = async (data) => {
    try {
      if (data.parent_id && data.parent_id !== "") {
        const parentCategory = categories.find(cat => cat.id === parseInt(data.parent_id));
        if (!parentCategory) {
          toast.error("Selected parent category not found");
          return;
        }
        
        if (parseInt(data.parent_id) === editingCategory.id) {
          toast.error("Category cannot be its own parent");
          return;
        }
        
        if (parentCategory.subcategories && parentCategory.subcategories.length >= 10) {
          toast.warning("Parent category already has maximum number of subcategories");
          return;
        }
      }

      const categoryData = {
        ...data,
        parent_id: data.parent_id && data.parent_id !== "" ? parseInt(data.parent_id) : null
      };
      
      await updateCategory(editingCategory.id, categoryData);
      toast.success(`Category "${data.name}" updated successfully`);
      setShowModal(false);
      setEditingCategory(null);
      reset();
      refetch();
    } catch (error) {
      const errorMessage = error.response?.data?.detail || "Failed to update category";
      toast.error(errorMessage);
    }
  };

  const handleDelete = async (category) => {
    const isParent = category.type === "parent";
    const hasSubcategories = category.hasSubcategories;
    const hasPosts = category.post_count > 0;

    let confirmMessage = `Are you sure you want to delete "${category.name}"?`;
    
    if (isParent && hasSubcategories) {
      confirmMessage += `\n\nThis will also delete ${category.subcategories.length} subcategories.`;
    }
    
    if (hasPosts) {
      confirmMessage += `\n\nThis category has ${category.post_count} posts that will be affected.`;
    }
    
    confirmMessage += "\n\nThis action cannot be undone.";

    if (window.confirm(confirmMessage)) {
      try {
        await deleteCategory(category.id);
        toast.success(`Category "${category.name}" deleted successfully`);
        refetch();
      } catch (error) {
        const errorMessage = error.response?.data?.detail || "Failed to delete category";
        toast.error(errorMessage);
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const getCategoryStats = () => {
    const parentCategories = categories.filter(cat => !cat.parent_id);
    const subcategories = categories.filter(cat => cat.parent_id);
    const totalPosts = flatCategories.reduce((sum, cat) => sum + (cat.post_count || 0), 0);
    
    return {
      parentCategories: parentCategories.length,
      subcategories: subcategories.length,
      totalCategories: categories.length,
      totalPosts
    };
  };

  const stats = getCategoryStats();

  if (loading) {
    return (
      <Content>
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Content>
    );
  }

  if (error) {
    return (
      <Content>
        <Alert color="danger" role="alert">
          Error loading categories: {error}
        </Alert>
      </Content>
    );
  }

  return (
    <>
      <Head title="Category Management" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>Category Management</BlockTitle>
            </BlockHeadContent>
            <BlockHeadContent>
              <BackTo link="/posts-list" icon="arrow-left" className="btn btn-dim btn-outline-primary">
                Back to Posts
              </BackTo>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Card>
            <div className="card-inner-group">
              <div className="card-inner position-relative card-tools-toggle mb-5">
                <div className="d-flex flex-column flex-sm-row gap-2 align-items-sm-center justify-content-sm-end">
                  <div className="form-control-wrap" style={{ minWidth: '200px' }}>
                    <div className="form-icon form-icon-right">
                      <Icon name="search" />
                    </div>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Search categories..."
                      value={searchText}
                      onChange={onFilterChange}
                    />
                  </div>
                  <Button 
                    onClick={() => {
                      setModalMode("create");
                      setShowModal(true);
                    }}
                    className="btn btn-dim btn-primary"
                  >
                    <Icon name="plus" className="me-1" />
                    <span>Add Category</span>
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="card-inner p-0 mt-3">
              <DataTableBody>
                  <DataTableHead>
                    <DataTableRow>
                      <span className="sub-text">Name</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Slug</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Description</span>
                    </DataTableRow>
                    <DataTableRow className="nk-tb-col-tools text-end">
                      <span className="sub-text">Action</span>
                    </DataTableRow>
                  </DataTableHead>
                  
                   {currentItems.length > 0 ? (
                    currentItems.map((category) => (
                      <React.Fragment key={category.id}>
                      <DataTableItem>
                        <DataTableRow>
                          <div className="tb-lead d-flex align-items-center" style={{ paddingLeft: `${category.level * 20}px` }}>
                            {category.type === "parent" && (
                              <Button color="light" size="sm" className="me-2"
                                onClick={() => toggleExpand(category.id)}
                                aria-label={expandedParents.has(category.id) ? "Collapse" : "Expand"}
                              >
                                <Icon name={expandedParents.has(category.id) ? "chevron-down" : "chevron-right"} />
                              </Button>
                            )}
                            {category.level > 0 && (
                              <span className="text-muted me-2">└─</span>
                            )}
                            <span className="title">{category.name}</span>
                            {category.type === "parent" && (
                              <span className="badge badge-outline-primary ms-2 text-xs">
                                Main Category
                              </span>
                            )}
                            {category.type === "subcategory" && (
                              <span className="badge badge-outline-info ms-2 text-xs">
                                Subcategory
                              </span>
                            )}
                            {category.hasSubcategories && (
                              <span className="badge badge-outline-success ms-2 text-xs">
                                {category.subcategories.length} subcategories
                              </span>
                            )}
                            {category.level > 0 && category.parent_name && (
                              <span className="text-muted ms-2 text-xs">
                                (under {category.parent_name})
                              </span>
                            )}
                          </div>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub text-primary">/{category.slug}</span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">
                            {category.description || <em className="text-muted">No description</em>}
                          </span>
                        </DataTableRow>
                        <DataTableRow className="nk-tb-col-tools">
                          <ul className="nk-tb-actions gx-1 my-n1">
                            <li className="me-n0">
                              <Button
                                color="primary"
                                size="sm"
                                className="btn-icon"
                                onClick={() => handleEdit(category)}
                                title="Edit Category"
                              >
                                <Icon name="edit" />
                              </Button>
                            </li>
                            {category.type === "parent" && category.hasSubcategories && (
                              <li className="me-n0">
                                <Button
                                  color="light"
                                  size="sm"
                                  className="btn-icon"
                                  onClick={() => toggleExpand(category.id)}
                                  title={expandedParents.has(category.id) ? "Hide subcategories" : "View subcategories"}
                                >
                                  <Icon name={expandedParents.has(category.id) ? "eye-off" : "eye"} />
                                </Button>
                              </li>
                            )}
                            <li className="me-n0">
                              <Button
                                color="danger"
                                size="sm"
                                className="btn-icon"
                                onClick={() => handleDelete(category)}
                                title="Delete Category"
                              >
                                <Icon name="trash" />
                              </Button>
                            </li>
                          </ul>
                        </DataTableRow>
                      </DataTableItem>
                      {category.type === "parent" && expandedParents.has(category.id) && (!category.hasSubcategories || category.subcategories.length === 0) && (
                        <DataTableItem key={`${category.id}-empty`}>
                          <DataTableRow>
                            <div className="tb-lead text-muted" style={{ paddingLeft: `${20}px` }}>
                              <em>No subcategories yet</em>
                            </div>
                          </DataTableRow>
                          <DataTableRow size="sm"></DataTableRow>
                          <DataTableRow size="sm"></DataTableRow>
                          <DataTableRow className="nk-tb-col-tools">
                            <ul className="nk-tb-actions gx-1 my-n1">
                              <li className="me-n0">
                                <Button
                                  color="primary"
                                  size="sm"
                                  className="btn-icon"
                                  onClick={() => {
                                    setModalMode("create");
                                    setShowModal(true);
                                    reset({ parent_id: category.id });
                                  }}
                                  title="Add Subcategory"
                                >
                                  <Icon name="plus" />
                                </Button>
                              </li>
                            </ul>
                          </DataTableRow>
                        </DataTableItem>
                      )}
                      </React.Fragment>
                    ))
                  ) : (
                    <div className="text-center py-4">
                      <Icon name="inbox" className="mb-2" style={{ fontSize: "2rem" }} />
                      <p>
                        {searchText ? "No categories match your search" : "No categories found"}
                      </p>
                      {!searchText && (
                        <Button color="primary" size="sm" onClick={() => {
                          setModalMode("create");
                          setShowModal(true);
                        }}>
                          <Icon name="plus" />
                          Create First Category
                        </Button>
                      )}
                    </div>
                  )}
                </DataTableBody>
            </div>
              
            {filteredCategories.length > itemPerPage && (
                <div className="card-inner">
                  <div className="nk-block-between-md g-3">
                    <div className="g">
                      <PaginationComponent
                        itemPerPage={itemPerPage}
                        totalItems={filteredCategories.length}
                        paginate={paginate}
                        currentPage={currentPage}
                      />
                    </div>
                    <div className="g">
                      <div className="pagination-goto d-flex justify-content-center justify-content-md-start gx-3">
                        <div>Page</div>
                        <div>
                          <select
                            className="form-select"
                            value={currentPage}
                            onChange={(e) => setCurrentPage(parseInt(e.target.value))}
                          >
                            {[...Array(totalPages)].map((_, i) => (
                              <option key={i + 1} value={i + 1}>
                                {i + 1}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div>of {totalPages}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
          </Card>
        </Block>

        {/* Unified Category Modal */}
        <Modal isOpen={showModal} toggle={handleModalClose} className="modal-dialog-centered" size="md">
          <ModalHeader
            toggle={handleModalClose}
            close={
              <button className="close" onClick={handleModalClose}>
                <Icon name="cross" />
              </button>
            }
          >
            {modalMode === "create" ? "Create New Category" : "Edit Category"}
          </ModalHeader>
          <ModalBody>
            <form onSubmit={handleSubmit(modalMode === "create" ? onCreateSubmit : onUpdateSubmit)}>
              <div className="form-group">
                <label className="form-label" htmlFor="category-name">
                  Category Name *
                </label>
                <div className="form-control-wrap">
                  <input
                    id="category-name"
                    type="text"
                    className="form-control"
                    {...register('name', {
                      required: "Category name is required",
                      minLength: { value: 1, message: "Name must be at least 1 character" },
                      maxLength: { value: 100, message: "Name must be less than 100 characters" }
                    })}
                    placeholder="Enter category name"
                  />
                  {errors.name && <span className="invalid">{errors.name.message}</span>}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="parent-category">
                  Parent Category
                </label>
                <div className="form-control-wrap">
                  <select
                    id="parent-category"
                    className="form-select"
                    {...register('parent_id')}
                  >
                    <option value="">
                      {modalMode === "create" ? "None (Create Main Category)" : "None (Make Main Category)"}
                    </option>
                    {getAvailableParentCategories(editingCategory?.id).map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name} {category.subcategories && category.subcategories.length > 0 && 
                          `(${category.subcategories.length} subcategories)`}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-note">
                  <em>
                    {watchedParentId && watchedParentId !== "" 
                      ? modalMode === "create" 
                        ? "This will create a subcategory under the selected parent."
                        : "This will make this category a subcategory under the selected parent."
                      : "Leave empty to create a main category that can have subcategories."}
                  </em>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="category-description">
                  Description
                </label>
                <div className="form-control-wrap">
                  <textarea
                    id="category-description"
                    className="form-control"
                    rows="3"
                    {...register('description')}
                    placeholder="Optional description for this category"
                  />
                </div>
              </div>

              {modalMode === "create" && (
                <div className="form-note">
                  <em>The URL slug will be automatically generated from the category name.</em>
                </div>
              )}
            </form>
          </ModalBody>
          <ModalFooter className="bg-light">
            <Button 
              color="primary" 
              type="submit" 
              onClick={handleSubmit(modalMode === "create" ? onCreateSubmit : onUpdateSubmit)} 
              disabled={modalMode === "create" ? createLoading : updateLoading}
            >
              {modalMode === "create" ? (
                createLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Creating...
                  </>
                ) : (
                  <>
                    <Icon name="plus" />
                    <span>Create Category</span>
                  </>
                )
              ) : (
                updateLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Updating...
                  </>
                ) : (
                  <>
                    <Icon name="edit" />
                    <span>Update Category</span>
                  </>
                )
              )}
            </Button>
            <Button 
              color="secondary" 
              onClick={handleModalClose} 
              disabled={modalMode === "create" ? createLoading : updateLoading}
            >
              Cancel
            </Button>
          </ModalFooter>
        </Modal>
      </Content>
    </>
  );
};

export default CategoryManagement; 