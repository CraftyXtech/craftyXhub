import React, { useState, useEffect } from "react";
import { Modal, ModalBody, Row, Col, Button, Card } from "reactstrap";
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
  const { register, handleSubmit, reset, formState: { errors } } = useForm();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [sm, updateSm] = useState(false);

  // API hooks
  const { categories, loading, error, refetch } = useGetCategories();
  const { createCategory, loading: createLoading } = useCreateCategory();
  const { updateCategory, loading: updateLoading } = useUpdateCategory();
  const { deleteCategory, loading: deleteLoading } = useDeleteCategory();

  // Flatten categories for display (parent + subcategories)
  const flattenCategories = (cats) => {
    const flattened = [];
    cats.forEach(category => {
      // Add parent category
      flattened.push({ ...category, level: 0, isParent: !category.parent_id });
      // Add subcategories with indentation
      if (category.subcategories && category.subcategories.length > 0) {
        category.subcategories.forEach(subcat => {
          flattened.push({ ...subcat, level: 1, isParent: false, parent_name: category.name });
        });
      }
    });
    return flattened;
  };

  const flatCategories = flattenCategories(categories);
  
  // Filter categories based on search
  const filteredCategories = flatCategories.filter(category =>
    category.name.toLowerCase().includes(searchText.toLowerCase()) ||
    category.slug.toLowerCase().includes(searchText.toLowerCase()) ||
    (category.parent_name && category.parent_name.toLowerCase().includes(searchText.toLowerCase()))
  );

  // Pagination
  const indexOfLastItem = currentPage * itemPerPage;
  const indexOfFirstItem = indexOfLastItem - itemPerPage;
  const currentItems = filteredCategories.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredCategories.length / itemPerPage);

  // Auto-generate slug from name
  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9 -]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  };

  // Handle search
  const onFilterChange = (e) => {
    setSearchText(e.target.value);
    setCurrentPage(1);
  };

  // Handle create category
  const onCreateSubmit = async (data) => {
    try {
      const categoryData = {
        ...data,
        slug: generateSlug(data.name),
        parent_id: data.parent_id && data.parent_id !== "" ? parseInt(data.parent_id) : null
      };
      
      await createCategory(categoryData);
      toast.success("Category created successfully");
      setShowCreateModal(false);
      reset();
      refetch();
    } catch (error) {
      toast.error("Failed to create category");
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setEditingCategory(null);
    reset();
  };

  // Handle edit category
  const handleEdit = (category) => {
    setEditingCategory(category);
    reset({
      name: category.name,
      description: category.description || '',
      parent_id: category.parent_id || ''
    });
    setShowEditModal(true);
  };

  // Handle update category
  const onUpdateSubmit = async (data) => {
    try {
      const categoryData = {
        ...data,
        parent_id: data.parent_id && data.parent_id !== "" ? parseInt(data.parent_id) : null
      };
      
      await updateCategory(editingCategory.id, categoryData);
      toast.success("Category updated successfully");
      setShowEditModal(false);
      setEditingCategory(null);
      reset();
      refetch();
    } catch (error) {
      toast.error("Failed to update category");
    }
  };

  // Handle delete category
  const handleDelete = async (category) => {
    if (window.confirm(`Are you sure you want to delete "${category.name}"? This action cannot be undone.`)) {
      try {
        await deleteCategory(category.id);
        toast.success("Category deleted successfully");
        refetch();
      } catch (error) {
        toast.error(error.response?.data?.detail || "Failed to delete category");
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Change page
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

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
        <div className="alert alert-danger" role="alert">
          Error loading categories: {error}
        </div>
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
              <BlockDes className="text-soft">
                <p>Manage your post categories and subcategories. You have {categories.length} parent categories total.</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <BackTo link="/posts-list" icon="arrow-left">
                Back to Posts
              </BackTo>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Card>
            <div className="card-inner-group">
              <div className="card-inner position-relative card-tools-toggle">
                <div className="card-title-group">
                  <div className="card-tools">
                    <div className="form-inline flex-nowrap gx-3">
                      <div className="form-wrap w-150px">
                        <select
                          className="form-select"
                          value={itemPerPage}
                          onChange={(e) => setItemPerPage(parseInt(e.target.value))}
                        >
                          <option value={10}>10 per page</option>
                          <option value={25}>25 per page</option>
                          <option value={50}>50 per page</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  <div className="card-tools me-n1">
                    <ul className="btn-toolbar gx-1">
                      <li>
                        <div className="form-control-wrap">
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
                      </li>
                      <li className="btn-toolbar-sep"></li>
                      <li>
                        <Button color="primary" onClick={() => setShowCreateModal(true)}>
                          <Icon name="plus" />
                          <span>Add Category</span>
                        </Button>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <div className="card-inner p-0">
                <DataTableBody>
                  <DataTableHead>
                    <DataTableRow>
                      <span className="sub-text">Name</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Slug</span>
                    </DataTableRow>
                    <DataTableRow size="md">
                      <span className="sub-text">Description</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Posts</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Created</span>
                    </DataTableRow>
                    <DataTableRow className="nk-tb-col-tools text-end">
                      <span className="sub-text">Action</span>
                    </DataTableRow>
                  </DataTableHead>
                  
                  {currentItems.length > 0 ? (
                    currentItems.map((category) => (
                      <DataTableItem key={category.id}>
                                              <DataTableRow>
                        <div className="tb-lead" style={{ paddingLeft: `${category.level * 20}px` }}>
                          {category.level > 0 && (
                            <span className="text-muted me-2">└─</span>
                          )}
                          <span className="title">{category.name}</span>
                          {category.isParent && category.subcategories?.length > 0 && (
                            <span className="badge badge-outline-info ms-2 text-xs">
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
                        <DataTableRow size="md">
                          <span className="tb-sub">
                            {category.description || <em className="text-muted">No description</em>}
                          </span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">
                            <span className="badge badge-outline-primary">
                              {category.post_count || 0} posts
                            </span>
                          </span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">{formatDate(category.created_at)}</span>
                        </DataTableRow>
                        <DataTableRow className="nk-tb-col-tools">
                          <ul className="nk-tb-actions gx-1 my-n1">
                            <li className="me-n1">
                              <div className="dropdown">
                                <a
                                  href="#more"
                                  className="dropdown-toggle btn btn-icon btn-trigger"
                                  data-bs-toggle="dropdown"
                                  onClick={(ev) => ev.preventDefault()}
                                >
                                  <Icon name="more-h" />
                                </a>
                                <div className="dropdown-menu dropdown-menu-end">
                                  <ul className="link-list-opt no-bdr">
                                    <li>
                                      <a 
                                        href="#edit" 
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleEdit(category);
                                        }}
                                      >
                                        <Icon name="edit" />
                                        <span>Edit Category</span>
                                      </a>
                                    </li>
                                    <li className="divider"></li>
                                    <li>
                                      <a 
                                        href="#delete" 
                                        className="text-danger"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleDelete(category);
                                        }}
                                      >
                                        <Icon name="trash" />
                                        <span>Delete Category</span>
                                      </a>
                                    </li>
                                  </ul>
                                </div>
                              </div>
                            </li>
                          </ul>
                        </DataTableRow>
                      </DataTableItem>
                    ))
                  ) : (
                    <div className="text-center py-4">
                      <Icon name="inbox" className="mb-2" style={{ fontSize: "2rem" }} />
                      <p>
                        {searchText ? "No categories match your search" : "No categories found"}
                      </p>
                      {!searchText && (
                        <Button color="primary" size="sm" onClick={() => setShowCreateModal(true)}>
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
            </div>
          </Card>
        </Block>

        {/* Create Category Modal */}
        <Modal isOpen={showCreateModal} toggle={handleModalClose} className="modal-dialog-centered" size="md">
          <ModalBody>
            <a href="#cancel" className="close">
              <Icon
                name="cross-sm"
                onClick={(ev) => {
                  ev.preventDefault();
                  handleModalClose();
                }}
              />
            </a>
            <div className="p-2">
              <h5 className="title">Create New Category</h5>
              <div className="mt-4">
                <form onSubmit={handleSubmit(onCreateSubmit)}>
                  <Row className="g-3">
                    <Col size="12">
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
                    </Col>

                    <Col size="12">
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
                            <option value="">None (Root Category)</option>
                            {categories.filter(cat => !cat.parent_id).map((category) => (
                              <option key={category.id} value={category.id}>
                                {category.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="form-note">
                          <em>Select a parent category to create a subcategory, or leave empty for a root category.</em>
                        </div>
                      </div>
                    </Col>

                    <Col size="12">
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
                    </Col>

                    <Col size="12">
                      <div className="form-note">
                        <em>The URL slug will be automatically generated from the category name.</em>
                      </div>
                    </Col>

                    <Col size="12">
                      <div className="form-group">
                        <Button color="primary" type="submit" disabled={createLoading}>
                          {createLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              Creating...
                            </>
                          ) : (
                            <>
                              <Icon name="plus" />
                              <span>Create Category</span>
                            </>
                          )}
                        </Button>
                        <Button color="secondary" className="ms-2" onClick={handleModalClose} disabled={createLoading}>
                          Cancel
                        </Button>
                      </div>
                    </Col>
                  </Row>
                </form>
              </div>
            </div>
          </ModalBody>
        </Modal>

        {/* Edit Category Modal */}
        <Modal isOpen={showEditModal} toggle={handleModalClose} className="modal-dialog-centered" size="md">
          <ModalBody>
            <a href="#cancel" className="close">
              <Icon
                name="cross-sm"
                onClick={(ev) => {
                  ev.preventDefault();
                  handleModalClose();
                }}
              />
            </a>
            <div className="p-2">
              <h5 className="title">Edit Category</h5>
              <div className="mt-4">
                <form onSubmit={handleSubmit(onUpdateSubmit)}>
                  <Row className="g-3">
                    <Col size="12">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-category-name">
                          Category Name *
                        </label>
                        <div className="form-control-wrap">
                          <input
                            id="edit-category-name"
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
                    </Col>

                    <Col size="12">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-parent-category">
                          Parent Category
                        </label>
                        <div className="form-control-wrap">
                          <select
                            id="edit-parent-category"
                            className="form-select"
                            {...register('parent_id')}
                          >
                            <option value="">None (Root Category)</option>
                            {categories.filter(cat => !cat.parent_id && cat.id !== editingCategory?.id).map((category) => (
                              <option key={category.id} value={category.id}>
                                {category.name}
                              </option>
                            ))}
                          </select>
                        </div>
                        <div className="form-note">
                          <em>Select a parent category to create a subcategory, or leave empty for a root category.</em>
                        </div>
                      </div>
                    </Col>

                    <Col size="12">
                      <div className="form-group">
                        <label className="form-label" htmlFor="edit-category-description">
                          Description
                        </label>
                        <div className="form-control-wrap">
                          <textarea
                            id="edit-category-description"
                            className="form-control"
                            rows="3"
                            {...register('description')}
                            placeholder="Optional description for this category"
                          />
                        </div>
                      </div>
                    </Col>

                    <Col size="12">
                      <div className="form-group">
                        <Button color="primary" type="submit" disabled={updateLoading}>
                          {updateLoading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                              Updating...
                            </>
                          ) : (
                            <>
                              <Icon name="edit" />
                              <span>Update Category</span>
                            </>
                          )}
                        </Button>
                        <Button color="secondary" className="ms-2" onClick={handleModalClose} disabled={updateLoading}>
                          Cancel
                        </Button>
                      </div>
                    </Col>
                  </Row>
                </form>
              </div>
            </div>
          </ModalBody>
        </Modal>
      </Content>
    </>
  );
};

export default CategoryManagement; 