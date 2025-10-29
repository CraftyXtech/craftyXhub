import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { UncontrolledDropdown, DropdownToggle, DropdownMenu, DropdownItem, Modal, ModalBody, FormGroup, Label, Input } from 'reactstrap';
import Head from '@/layout/head/Head';
import Content from '@/layout/content/Content';
import { Block, BlockHead, BlockTitle, BlockDes, BlockBetween, BlockHeadContent, Button, Icon, ReactDataTable } from '@/components/Component';
import { useAiDocuments } from '@/context/AiDocumentContext';
import { textUtils } from '@/utils/textUtils';
import { toast } from 'react-toastify';

const AiDocuments = () => {
  const navigate = useNavigate();
  const { documents, deleteDocument, duplicateDocument, updateDocument, exportDocuments } = useAiDocuments();
  const [selectedRows, setSelectedRows] = useState([]);
  const [renameModal, setRenameModal] = useState(false);
  const [currentDoc, setCurrentDoc] = useState(null);
  const [newName, setNewName] = useState('');

  const handleRename = (doc) => {
    setCurrentDoc(doc);
    setNewName(doc.name);
    setRenameModal(true);
  };

  const handleRenameSubmit = () => {
    if (currentDoc && newName.trim()) {
      updateDocument(currentDoc.id, { name: newName.trim() });
      setRenameModal(false);
      setCurrentDoc(null);
      setNewName('');
    }
  };

  const handlePromoteToPost = (doc) => {
    navigate('/posts-create', {
      state: {
        fromAiDocument: true,
        title: doc.name,
        content: doc.content,
        excerpt: textUtils.generateExcerpt(doc.content),
        reading_time: doc.metadata?.readingTime || textUtils.estimateReadingTime(doc.content)
      }
    });
  };

  const columns = [
    {
      name: 'Name',
      selector: (row) => row.name,
      sortable: true,
      cell: (row) => (
        <div className="user-card">
          <div className="user-info">
            <span className="tb-lead">{row.name}</span>
            <span className="sub-text">{row.metadata?.words || textUtils.countWords(row.content)} words</span>
          </div>
        </div>
      ),
    },
    {
      name: 'Type',
      selector: (row) => row.type,
      sortable: true,
      cell: (row) => (
        <span className="badge badge-dim badge-sm badge-primary">
          {row.type || 'Blog Post'}
        </span>
      ),
    },
    {
      name: 'Last Modified',
      selector: (row) => row.updated_at,
      sortable: true,
      cell: (row) => textUtils.formatDateTime(row.updated_at),
    },
    {
      name: 'Actions',
      cell: (row) => (
        <UncontrolledDropdown>
          <DropdownToggle tag="a" className="dropdown-toggle btn btn-sm btn-icon btn-trigger">
            <Icon name="more-h"></Icon>
          </DropdownToggle>
          <DropdownMenu end>
            <ul className="link-list-opt no-bdr">
              <li>
                <DropdownItem
                  tag="a"
                  href="#edit"
                  onClick={(ev) => {
                    ev.preventDefault();
                    navigate(`/ai-writer/editor/${row.id}`);
                  }}
                >
                  <Icon name="edit"></Icon>
                  <span>Edit</span>
                </DropdownItem>
              </li>
              <li>
                <DropdownItem
                  tag="a"
                  href="#rename"
                  onClick={(ev) => {
                    ev.preventDefault();
                    handleRename(row);
                  }}
                >
                  <Icon name="pen"></Icon>
                  <span>Rename</span>
                </DropdownItem>
              </li>
              <li>
                <DropdownItem
                  tag="a"
                  href="#duplicate"
                  onClick={(ev) => {
                    ev.preventDefault();
                    duplicateDocument(row.id);
                  }}
                >
                  <Icon name="copy"></Icon>
                  <span>Duplicate</span>
                </DropdownItem>
              </li>
              <li>
                <DropdownItem
                  tag="a"
                  href="#promote"
                  onClick={(ev) => {
                    ev.preventDefault();
                    handlePromoteToPost(row);
                  }}
                >
                  <Icon name="upload-cloud"></Icon>
                  <span>Promote to Post</span>
                </DropdownItem>
              </li>
              <li className="divider"></li>
              <li>
                <DropdownItem
                  tag="a"
                  href="#delete"
                  onClick={(ev) => {
                    ev.preventDefault();
                    if (window.confirm('Are you sure you want to delete this document?')) {
                      deleteDocument(row.id);
                    }
                  }}
                >
                  <Icon name="trash"></Icon>
                  <span>Delete</span>
                </DropdownItem>
              </li>
            </ul>
          </DropdownMenu>
        </UncontrolledDropdown>
      ),
      sortable: false,
    },
  ];

  return (
    <>
      <Head title="AI Documents" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>AI Documents</BlockTitle>
              <BlockDes className="text-soft">
                <p>Manage your AI-generated content</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="toggle-wrap nk-block-tools-toggle">
                <div className="toggle-expand-content">
                  <ul className="nk-block-tools g-3">
                    <li>
                      <Button color="light" outline onClick={exportDocuments}>
                        <Icon name="download" />
                        <span>Export</span>
                      </Button>
                    </li>
                    <li>
                      <Button color="primary" onClick={() => navigate('/ai-writer/editor/new')}>
                        <Icon name="plus" />
                        <span>New Document</span>
                      </Button>
                    </li>
                  </ul>
                </div>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          {documents.length === 0 ? (
            <div className="text-center py-5 card card-bordered">
              <div className="card-inner">
                <Icon name="file-text" className="text-soft mb-2" style={{ fontSize: '3rem' }} />
                <h6 className="mb-2">No documents yet</h6>
                <p className="text-soft mb-3">Start creating AI-powered content now</p>
                <Button color="primary" onClick={() => navigate('/ai-writer/editor/new')}>
                  <Icon name="spark" className="me-1" />
                  <span>Generate Content</span>
                </Button>
              </div>
            </div>
          ) : (
            <ReactDataTable
              data={documents}
              columns={columns}
              pagination
              className="nk-tb-list"
              selectableRows
              onSelectedRowsChange={(state) => setSelectedRows(state.selectedRows)}
            />
          )}
        </Block>
      </Content>

      <Modal isOpen={renameModal} toggle={() => setRenameModal(false)}>
        <ModalBody>
          <a
            href="#cancel"
            onClick={(ev) => {
              ev.preventDefault();
              setRenameModal(false);
            }}
            className="close"
          >
            <Icon name="cross-sm"></Icon>
          </a>
          <div className="p-2">
            <h5 className="title">Rename Document</h5>
            <div className="mt-4">
              <FormGroup>
                <Label className="form-label">Document Name</Label>
                <Input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Enter document name"
                />
              </FormGroup>
              <div className="form-group mt-3">
                <Button color="primary" size="lg" onClick={handleRenameSubmit}>
                  Save Changes
                </Button>
                <Button color="light" size="lg" className="ms-2" onClick={() => setRenameModal(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </ModalBody>
      </Modal>
    </>
  );
};

export default AiDocuments;

