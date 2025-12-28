import { Pagination as MuiPagination, Box } from '@mui/material';

/**
 * Pagination - Styled pagination component
 */
export default function Pagination({ 
  count = 1, 
  page = 1, 
  onChange = () => {},
  sx = {}
}) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5, ...sx }}>
      <MuiPagination
        count={count}
        page={page}
        onChange={onChange}
        color="primary"
        shape="rounded"
        showFirstButton
        showLastButton
        sx={{
          '& .MuiPaginationItem-root': {
            fontWeight: 500
          }
        }}
      />
    </Box>
  );
}
