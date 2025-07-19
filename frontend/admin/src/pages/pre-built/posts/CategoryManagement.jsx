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
import { useGetCategories, useCreateCategory } from "@/api/postService";
import { toast } from "react-toastify";

const CategoryManagement = () => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [sm, updateSm] = useState(false);

  // API hooks
  const { categories, loading, error, refetch } = useGetCategories();
  const { createCategory, loading: createLoading } = useCreateCategory();

  // Filter categories based on search
  const filteredCategories = categories.filter(category =>
    category.name.toLowerCase().includes(searchText.toLowerCase()) ||
    category.slug.toLowerCase().includes(searchText.toLowerCase())
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
        slug: generateSlug(data.name)
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
    reset();
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
                <p>Manage your post categories. You have {categories.length} categories total.</p>
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
                          <div className="tb-lead">
                            <span className="title">{category.name}</span>
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
                                      <a href="#view" onClick={(ev) => ev.preventDefault()}>
                                        <Icon name="eye" />
                                        <span>View Details</span>
                                      </a>
                                    </li>
                                    <li className="divider"></li>
                                    <li>
                                      <a 
                                        href="#edit" 
                                        className="text-muted"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          toast.info("Edit functionality requires backend API extension");
                                        }}
                                      >
                                        <Icon name="edit" />
                                        <span>Edit (Not Available)</span>
                                      </a>
                                    </li>
                                    <li>
                                      <a 
                                        href="#delete" 
                                        className="text-muted"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          toast.info("Delete functionality requires backend API extension");
                                        }}
                                      >
                                        <Icon name="trash" />
                                        <span>Delete (Not Available)</span>
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

        {/* API Limitation Notice */}
        <Block>
          <Card className="card-bordered">
            <div className="card-inner">
              <div className="alert alert-info d-flex align-items-center">
                <Icon name="info" className="me-2" />
                <div>
                  <strong>API Limitation Notice:</strong> Currently, only category creation and listing are supported. 
                  Edit and delete functionality require additional backend API endpoints 
                  (<code>PUT /posts/categories/{`{id}`}</code> and <code>DELETE /posts/categories/{`{id}`}</code>).
                </div>
              </div>
            </div>
          </Card>
        </Block>
      </Content>
    </>
  );
};

export default CategoryManagement; 