import { useEffect, useMemo, useState } from 'react';
import {
  Card, Table, TableHead, TableRow, TableCell, TableBody, TextField, MenuItem, Stack,
  InputAdornment, TablePagination, LinearProgress, TableSortLabel,
} from '@mui/material';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as claimsService from '../services/claimsService';
import { useNavigate } from 'react-router-dom';
import { useAuth, ROLES } from '../context/AuthContext';

export default function ClaimHistory() {
  const { user } = useAuth();
  const isPolicyholder = user?.role === ROLES.POLICYHOLDER;
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [risk, setRisk] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState('claimDate');
  const [sortDir, setSortDir] = useState('desc');
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    // Policyholders only ever see claims they submitted themselves.
    const params = isPolicyholder ? { search, risk, status, ownerId: user.id } : { search, risk, status };
    claimsService.getClaims(params).then((data) => {
      setClaims(data);
      setLoading(false);
      setPage(0);
    });
  }, [search, risk, status, isPolicyholder, user?.id]);

  const sorted = useMemo(() => {
    const arr = [...claims];
    const getVal = (c) => {
      switch (sortBy) {
        case 'amount': return c.financial.claimAmount;
        case 'risk': return c.prediction.probability;
        case 'claimDate': return c.dates.claimDate;
        default: return c.id;
      }
    };
    arr.sort((a, b) => {
      const av = getVal(a), bv = getVal(b);
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return arr;
  }, [claims, sortBy, sortDir]);

  const paged = sorted.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const toggleSort = (col) => {
    if (sortBy === col) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortBy(col); setSortDir('desc'); }
  };

  return (
    <DashboardLayout title={isPolicyholder ? 'My Claims' : 'Claim History'}>
      <Card sx={{ p: 2.5 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ mb: 2 }}>
          <TextField
            placeholder="Search claim ID, patient, or provider"
            size="small" fullWidth value={search} onChange={(e) => setSearch(e.target.value)}
            InputProps={{ startAdornment: <InputAdornment position="start"><SearchOutlinedIcon fontSize="small" /></InputAdornment> }}
          />
          <TextField select size="small" label="Risk" value={risk} onChange={(e) => setRisk(e.target.value)} sx={{ minWidth: 140 }}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="High">High</MenuItem>
            <MenuItem value="Medium">Medium</MenuItem>
            <MenuItem value="Low">Low</MenuItem>
          </TextField>
          <TextField select size="small" label="Status" value={status} onChange={(e) => setStatus(e.target.value)} sx={{ minWidth: 170 }}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="Approved">Approved</MenuItem>
            <MenuItem value="Pending Review">Pending Review</MenuItem>
            <MenuItem value="Under Investigation">Under Investigation</MenuItem>
            <MenuItem value="Rejected">Rejected</MenuItem>
          </TextField>
        </Stack>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {!loading && sorted.length === 0 ? (
          <EmptyState
            title={isPolicyholder ? 'No claims yet' : 'No claims match your filters'}
            description={isPolicyholder ? 'Claims you submit will appear here.' : 'Try adjusting your search or filters.'}
          />
        ) : (
          <>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel active={sortBy === 'id'} direction={sortDir} onClick={() => toggleSort('id')}>Claim Number</TableSortLabel>
                  </TableCell>
                  <TableCell>Patient</TableCell>
                  <TableCell>
                    <TableSortLabel active={sortBy === 'amount'} direction={sortDir} onClick={() => toggleSort('amount')}>Amount</TableSortLabel>
                  </TableCell>
                  <TableCell>Prediction</TableCell>
                  <TableCell>
                    <TableSortLabel active={sortBy === 'risk'} direction={sortDir} onClick={() => toggleSort('risk')}>Risk</TableSortLabel>
                  </TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>
                    <TableSortLabel active={sortBy === 'claimDate'} direction={sortDir} onClick={() => toggleSort('claimDate')}>Created Date</TableSortLabel>
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paged.map((c) => (
                  <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => navigate(`/claims/${c.id}`)}>
                    <TableCell sx={{ fontWeight: 600 }}>{c.id}</TableCell>
                    <TableCell>{c.patient.name}</TableCell>
                    <TableCell>${c.financial.claimAmount.toLocaleString()}</TableCell>
                    <TableCell>{c.prediction.label}</TableCell>
                    <TableCell><RiskChip level={c.prediction.riskLevel} /></TableCell>
                    <TableCell><StatusChip status={c.status} /></TableCell>
                    <TableCell>{c.dates.claimDate}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <TablePagination
              component="div"
              count={sorted.length}
              page={page}
              onPageChange={(e, p) => setPage(p)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => { setRowsPerPage(Number(e.target.value)); setPage(0); }}
              rowsPerPageOptions={[10, 25, 50]}
            />
          </>
        )}
      </Card>
    </DashboardLayout>
  );
}
