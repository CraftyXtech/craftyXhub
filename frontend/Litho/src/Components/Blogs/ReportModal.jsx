import React, { useState, memo } from 'react'
import PropTypes from "prop-types"

// Libraries
import { Modal, Form, Button, Alert } from 'react-bootstrap'
import { Formik } from 'formik'
import * as Yup from 'yup'
import { m } from "framer-motion"

// API & Auth
import { useReportPost } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// CSS
import "../../Assets/scss/components/_report-modal.scss"

const ReportModal = (props) => {
  const { 
    show, 
    onHide, 
    postUuid, 
    postTitle,
    onReportSuccess,
    ...restProps 
  } = props;

  const [reportSubmitted, setReportSubmitted] = useState(false);
  
  const { isAuthenticated } = useAuth();
  const { reportPostAction, loading, error } = useReportPost();

  // Report reason options
  const reportReasons = [
    { value: 'spam', label: 'Spam or unwanted content' },
    { value: 'harassment', label: 'Harassment or bullying' },
    { value: 'hate_speech', label: 'Hate speech or discrimination' },
    { value: 'violence', label: 'Violence or threats' },
    { value: 'misinformation', label: 'False or misleading information' },
    { value: 'copyright', label: 'Copyright infringement' },
    { value: 'inappropriate', label: 'Inappropriate content' },
    { value: 'other', label: 'Other (please specify)' }
  ];

  // Form validation schema
  const validationSchema = Yup.object().shape({
    reason: Yup.string()
      .required('Please select a reason for reporting'),
    description: Yup.string()
      .when('reason', {
        is: 'other',
        then: (schema) => schema.required('Please specify the reason'),
        otherwise: (schema) => schema.min(10, 'Please provide more details (minimum 10 characters)')
      })
      .max(500, 'Description must be less than 500 characters')
  });

  const handleSubmit = async (values, { setSubmitting, setFieldError }) => {
    if (!isAuthenticated) {
      setFieldError('reason', 'You must be logged in to report posts');
      return;
    }

    try {
      await reportPostAction(postUuid, {
        reason: values.reason,
        description: values.description || undefined
      });
      
      setReportSubmitted(true);
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        onHide();
        setReportSubmitted(false);
        if (onReportSuccess) {
          onReportSuccess();
        }
      }, 2000);
      
    } catch (err) {
      console.error('Error submitting report:', err);
      setFieldError('reason', 'Failed to submit report. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setReportSubmitted(false);
    onHide();
  };

  if (!isAuthenticated) {
    return (
      <Modal 
        show={show} 
        onHide={handleClose}
        centered
        className="report-modal"
        {...restProps}
      >
        <Modal.Header closeButton>
          <Modal.Title className="font-serif text-darkgray">
            <i className="feather-shield mr-2"></i>
            Authentication Required
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="text-center py-4">
            <i className="feather-lock text-4xl text-spanishgray mb-3"></i>
            <p className="text-spanishgray mb-0">
              You must be logged in to report posts.
            </p>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }

  return (
    <Modal 
      show={show} 
      onHide={handleClose}
      centered
      size="md"
      className="report-modal"
      {...restProps}
    >
      <Modal.Header closeButton>
        <Modal.Title className="font-serif text-darkgray">
          <i className="feather-flag mr-2 text-red-500"></i>
          Report Post
        </Modal.Title>
      </Modal.Header>
      
      {reportSubmitted ? (
        <m.div {...fadeIn}>
          <Modal.Body>
            <div className="text-center py-4">
              <m.i 
                className="feather-check-circle text-5xl text-green-500 mb-4"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
              ></m.i>
              <h4 className="font-serif text-darkgray mb-3">Report Submitted</h4>
              <p className="text-spanishgray mb-0">
                Thank you for helping keep our community safe. We'll review your report and take appropriate action.
              </p>
            </div>
          </Modal.Body>
        </m.div>
      ) : (
        <Formik
          initialValues={{
            reason: '',
            description: ''
          }}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ values, errors, touched, handleChange, handleBlur, handleSubmit, isSubmitting }) => (
            <Form onSubmit={handleSubmit}>
              <Modal.Body>
                {postTitle && (
                  <div className="bg-lightgray p-3 rounded mb-4">
                    <h6 className="font-serif text-darkgray mb-1">Reporting Post:</h6>
                    <p className="text-spanishgray text-sm mb-0">{postTitle}</p>
                  </div>
                )}
                
                {error && (
                  <Alert variant="danger" className="mb-4">
                    <i className="feather-alert-triangle mr-2"></i>
                    {error}
                  </Alert>
                )}
                
                <div className="mb-4">
                  <Form.Label className="font-medium text-darkgray mb-2">
                    Why are you reporting this post? <span className="text-red-500">*</span>
                  </Form.Label>
                  <Form.Select
                    name="reason"
                    value={values.reason}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    isInvalid={touched.reason && errors.reason}
                    className="form-control"
                  >
                    <option value="">Select a reason...</option>
                    {reportReasons.map(reason => (
                      <option key={reason.value} value={reason.value}>
                        {reason.label}
                      </option>
                    ))}
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">
                    {errors.reason}
                  </Form.Control.Feedback>
                </div>
                
                <div className="mb-4">
                  <Form.Label className="font-medium text-darkgray mb-2">
                    Additional Details {values.reason === 'other' && <span className="text-red-500">*</span>}
                  </Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    name="description"
                    value={values.description}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    isInvalid={touched.description && errors.description}
                    placeholder={values.reason === 'other' ? 'Please specify the reason for reporting...' : 'Provide any additional context that might help us review this report...'}
                    maxLength={500}
                  />
                  <Form.Control.Feedback type="invalid">
                    {errors.description}
                  </Form.Control.Feedback>
                  <div className="text-right text-xs text-spanishgray mt-1">
                    {values.description.length}/500 characters
                  </div>
                </div>
                
                <div className="bg-lightgray p-3 rounded">
                  <p className="text-xs text-spanishgray mb-2">
                    <i className="feather-info mr-1"></i>
                    <strong>Note:</strong> False reports may result in restrictions on your account. 
                    Only report content that violates our community guidelines.
                  </p>
                </div>
              </Modal.Body>
              
              <Modal.Footer>
                <Button 
                  variant="secondary" 
                  onClick={handleClose}
                  disabled={isSubmitting || loading}
                >
                  Cancel
                </Button>
                <Button 
                  variant="danger" 
                  type="submit"
                  disabled={isSubmitting || loading || !values.reason}
                  className="btn-report"
                >
                  {(isSubmitting || loading) && (
                    <i className="feather-loader animate-spin mr-2"></i>
                  )}
                  {isSubmitting || loading ? 'Submitting...' : 'Submit Report'}
                </Button>
              </Modal.Footer>
            </Form>
          )}
        </Formik>
      )}
    </Modal>
  )
}

ReportModal.defaultProps = {
  show: false,
  postTitle: null,
  onReportSuccess: null
}

ReportModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  postUuid: PropTypes.string.isRequired,
  postTitle: PropTypes.string,
  onReportSuccess: PropTypes.func,
}

export default memo(ReportModal)