import sys
import re
import string
import traceback
import collections
import pdb
BLANK = ' '
LINE_BREAK = '\n'
TAB = '\t'
EQUAL = '='
SEMICOLON = ';'
DISTINCT = 'distinct'
DESC = 'desc'
ASC = 'asc'
AS = 'as'
JOIN = 'join'
ALL_JOINS = [i+JOIN for i in ['natural ', 'left ', 'right ', 'inner ', 'outer ', '']]
ON = 'on'

SELECT = 'select'
FROM = 'from'
WHERE = 'where'
ORDER_BY = 'order by'
GROUP_BY = 'group by'

keywords = [SELECT, FROM, WHERE, ORDER_BY, GROUP_BY]
colors = ["#00FFFF", "#808080", "#FFFF00", "#008000", "#808000", "#008080", "#0000FF", "#00FF00", "#800080", "#FF00FF", "#800000"]
color_names = ["aqua", "grey", "yellow", "green", "olive", "teal", "blue", "lime", "purple", "fuchsia", "maroon"]
colors_map = dict(zip(color_names, colors))

class DisplayUnit:

    def __init__(self, id_str, text, matchable, qep_id=-1, color=''):
        self.id = id_str
        self.text = text
        self.matchable = matchable
        self.qep_id = qep_id
        self.color = color

    def __str__(self):
        return "Display{id:%s, text:%s, matchable:%s, qepid:%s, color:%s}" % (self.id, self.text, self.matchable, self.qep_id, self.color)


class Relation:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Relation{%s}" % self.name


class JoinRelation(Relation):

    def __init__(self, left, right, condition_left, condition_right, join_type=JOIN):
        Relation.__init__(self, "join")
        self.relation_left = left
        self.relation_right = right
        self.product = False
        self.condition_left_attr = condition_left
        self.condition_right_attr = condition_right
        self.join_type = join_type

    def __str__(self):
        return "%s{ %s & %s with condition [ %s ] = [ %s ] }" % \
               (self.join_type, self.relation_left, self.relation_right, self.condition_left_attr, self.condition_right_attr)

def reconstruct_relations_compare(cur_id, unit_lst, join_node, qep_root):
    if 'relation_left' not in join_node.__dict__.keys():
        unit_lst.append(DisplayUnit("sqlu-"+next(cur_id), join_node.name, False))
    if not isinstance(join_node.relation_left, JoinRelation):
        cur_text = join_node.relation_left.name
    else:
        cur_text = "   "
        reconstruct_relations(cur_id, unit_lst, join_node.relation_left, qep_root)
    if 'natural' in join_node.join_type: # no ON condition in natural join
        cur_text += " {} ".format(join_node.join_type.upper()) + join_node.relation_right.name
    else:
        cur_text += " {} ".format(join_node.join_type.upper()) + join_node.relation_right.name + " ON " + join_node.condition_left_attr + " = " + join_node.condition_right_attr
    unit_lst.append(DisplayUnit("sqlu-"+next(cur_id), cur_text, False))

def reconstruct_relations(cur_id, unit_lst, join_node, qep_root):
    if 'relation_left' not in join_node.__dict__.keys():
        unit_lst.append(DisplayUnit("sqlu-"+str(cur_id), join_node.name, False))
        return cur_id + 1
    if not isinstance(join_node.relation_left, JoinRelation):
        cur_text = join_node.relation_left.name
    else:
        cur_text = "   "
        cur_id = reconstruct_relations(cur_id, unit_lst, join_node.relation_left, qep_root)
    if 'natural' in self.JOIN_WORD: # no ON condition in natural join
        cur_text += " {} ".format(self.JOIN_WORD.uper()) + join_node.relation_right.name
    else:
        cur_text += " {} ".format(self.JOIN_WORD.uper()) + join_node.relation_right.name + " ON " + join_node.condition_left_attr + " = " + join_node.condition_right_attr
    unit_lst.append(DisplayUnit("sqlu-"+str(cur_id), cur_text, True, qep_root.search_join_id(join_node)))
    return cur_id + 1


class WhereExpression:

    def __init__(self, left, right, op, relation):
        self.left = left
        self.right = right
        self.relation = relation
        self.op = op

    def __str__(self):
        return "WHERE_EXP{ %s %s %s (Relation{%s}) }" % (self.left, self.op, self.right, self.relation)

    def reconstruct_str(self):
        cur_text = ""
        if self.relation:
            cur_text = self.relation + '.'
        cur_text += self.left + " " + self.op + " " + self.right
        return cur_text

class Projection:

    def __init__(self):
        self.attr = ''
        self.name_as = ''
        self.relation = ''

    def __str__(self):
        return "Projection{ attribute: " + self.attr + ", in: " + self.relation + ", as: " + self.name_as + "}"


class OrderCondition:

    def __init__(self, attr, desc, relation):
        self.attr = attr
        self.desc = desc
        self.relation = relation

    def __str__(self):
        op = ''
        if self.desc:
            op = 'DESC'
        return "OrderBy{ %s %s (Relation{%s})}" % (self.attr, op, self.relation)


class AggregationAttr:

    def __init__(self, attr, relation):
        self.attr = attr
        self.relation = relation

    def __str__(self):
        return "GroupBy{ %s (Relation{%s})}" % (self.attr, self.relation)


def search_cond(qep_node, cond):
    if qep_node.Node_Type == "Seq Scan" and "Filter" in qep_node.__dict__.keys():
        if cond.left in qep_node.Filter and cond.right in qep_node.Filter and cond.op in qep_node.Filter:
            return qep_node.id
    for c in qep_node.get_children():
        r = search_cond(c, cond)
        if r > -1:
            return r
    return -1


def search_order(qep_node, order_by, parent_unique, ow=False):
    if not parent_unique and qep_node.Node_Type == "Sort":
        s_str = order_by.attr
        if order_by.desc:
            s_str += " DESC"
        for sk in qep_node.Sort_Key:
            if s_str in sk:
                return qep_node.id
    parent_unique = (qep_node.Node_Type == "Unique")
    if ow:
        parent_unique = False
    for c in qep_node.get_children():
        r = search_order(c, order_by, parent_unique, ow)
        if r > -1:
            return r
    return -1


def search_group_by(qep_node, group_by):
    if qep_node.Node_Type == "Aggregate":
        if "Group_Key" in qep_node.__dict__.keys() and group_by.attr in qep_node.Group_Key:
            return qep_node.id
    for c in qep_node.get_children():
        r = search_group_by(c, group_by)
        if r > -1:
            return r
    return -1


class SQLParser:

    def __init__(self, data=""):
        assert isinstance(data, str)
        self.data = data.lower().strip(' ').strip(';').strip(' ')
        self.length = len(self.data)
        self.distinct = False
        self.index = 0
        self.join_count = 0
        self.projections_lst = []
        self.conditions_lst = []
        self.relations_lst = []
        self.order_cond_lst = []
        self.aggr_attr_lst = []

    def _cur(self):
        return self.data[self.index]

    def _eof(self):
        return self.index >= self.length

    def _trim_blank(self):
        while not self._eof() and self._cur().isspace():
            self.index += 1

    def _next_ws(self):
        idx = self.index
        while idx < self.length and not self.data[idx].isspace():
            idx += 1
        return idx

    def _read_until(self, sub_str):
        idx = self.data.find(sub_str, self.index)
        if idx != -1:
            content = self.data[self.index:idx+len(sub_str)]
            self.index = idx + len(sub_str)
            return content
        raise ValueError("expect [%s], not found" % sub_str)

    def _read_util_line_break(self):
        return self._read_until(LINE_BREAK)

    def _read_until_ws(self):
        self._trim_blank()
        ws_idx = self._next_ws()
        # print("next ws:"+str(ws_idx))
        content = self.data[self.index:ws_idx]
        self.index = ws_idx+1
        return content

    def _read_until_ws_or(self, sub_str):
        stop_substr = True
        self._trim_blank()
        idx = self.data.find(sub_str, self.index)
        cur_len = len(sub_str)
        ws_idx = self._next_ws()
        if idx == -1 or ws_idx < idx:
            stop_substr = False
            idx = ws_idx
            cur_len = 1
        content = self.data[self.index:idx]
        self.index = idx + cur_len
        return content, stop_substr

    def _expect_str_return(self, sub_str):
        self._trim_blank()
        if self.data[self.index:].startswith(sub_str) and (self.index+len(sub_str) == self.length or self.data[self.index+len(sub_str)] in [" ", ","]):
            self.index += len(sub_str)
            return sub_str
        return False

    def _expect_str(self, sub_str):
        self._trim_blank()
        if self.data[self.index:].startswith(sub_str) and (self.index+len(sub_str) == self.length or self.data[self.index+len(sub_str)] in [" ", ","]):
            self.JOIN_WORD = sub_str
            self.index += len(sub_str)
            return True
        return False

    def _expect_str_wild(self, sub_str):
        self._trim_blank()
        if self.data[self.index:].startswith(sub_str):
            self.index += len(sub_str)
            return True
        return False

    def _expect_keyword(self):
        self._trim_blank()
        for kw in keywords:
            if self.data[self.index:].startswith(kw):
                self.index += len(kw)
                return kw
        if not self._eof():
            raise ValueError("expect keyword, got [%s]" % self._read_util_line_break())
        return None

    def _test_keyword(self):
        self._trim_blank()
        for kw in keywords:
            if self.data[self.index:].startswith(kw) and self.data[self.index+len(kw)] == " ":
                return True
        return False

    def _next_keyword_idx(self):
        idx = self.length
        for kw in keywords:
            kw_idx = self.data.find(kw, self.index)
            if kw_idx > -1:
                idx = min(idx, kw_idx)
        return idx

    def _parse_select(self):
        if self._expect_str(DISTINCT):
            self.distinct = True
        while not self._eof() and not self._test_keyword():
            cur_proj = Projection()
            cur_name, _ = self._read_until_ws_or(',')
            split_idx = cur_name.find('.')
            if split_idx != -1:
                cur_proj.relation = cur_name[:split_idx]
                cur_proj.attr = cur_name[split_idx+1:]
            else:
                cur_proj.attr = cur_name
            if self._expect_str(AS):
                cur_proj.name_as, _ = self._read_until_ws_or(',')
            self.projections_lst.append(cur_proj)

    def _parse_relations(self):
        """
        Only allow JOIN with explicit condition
        :return:
        """
        self._trim_blank()
        prev_r = None
        pass_comma = False
        while not self._eof() and not self._test_keyword():
            # self._trim_blank()
            while not self._eof() and not self._test_keyword():
                if prev_r is None:
                    cur_relation_name, pass_comma = self._read_until_ws_or(',')
                    prev_r = Relation(cur_relation_name)
                
                i, join_type = 0, False
                while join_type == False and i < len(ALL_JOINS):
                    join_type = self._expect_str_return(ALL_JOINS[i])
                    i += 1

                if join_type != False:
                    join_relation_name, _ = self._read_until_ws_or(',')
                    join_r = Relation(join_relation_name)
                    if 'natural' not in join_type and self._expect_str(ON):
                        condition_left = self._read_until('=').strip().strip('=').strip()
                        condition_right, pass_comma = self._read_until_ws_or(',')
                        cur_r = JoinRelation(prev_r, join_r, condition_left, condition_right, join_type)
                        prev_r = cur_r
                    elif 'natural' in join_type:
                        cur_r = JoinRelation(prev_r, join_r, '', '', join_type)
                        prev_r = cur_r
                    #else:
                        #raise ValueError('Not Allowed: Join without condition')
                # print("current idx %s char %s" % (str(self.index), str(self.data[self.index-1])))
                if pass_comma or self._expect_str_wild(','):
                    self.relations_lst.append(prev_r)
                    prev_r = None
                    pass_comma = False
                    break
        self.relations_lst.append(prev_r)

    def _parse_where(self):
        self._trim_blank()
        end_idx = self._next_keyword_idx()
        condition_str = self.data[self.index:end_idx]
        self.index = end_idx
        if condition_str.find(' and ') != -1:
            conditions = condition_str.split(' and ')
        else:
            conditions = [condition_str]
        if conditions:
            for c in conditions:
                exprs = c.strip().split(' or ')
                for e in exprs:
                    match = re.search('[<=>]+', e)
                    if match:
                        relation = ''
                        left = e[:match.start()].strip()
                        right = e[match.end():].strip()
                        if left.find('.') != -1:
                            relation = left.split('.')[0]
                            left = left.split('.')[-1]
                        elif right.find('.') != -1:
                            relation = right.split('.')[0]
                            left = right.split('.')[-1]
                        self.conditions_lst.append(WhereExpression(left, right, match.group(), relation))

    def _parse_order_by(self):
        self._trim_blank()
        while not self._eof() and not self._test_keyword():
            attr_name, _ = self._read_until_ws_or(',')
            self._trim_blank()
            op = self._expect_str(DESC)
            if not op:
                self._expect_str(ASC)
            self._trim_blank()
            self._expect_str_wild(',')
            relation = ''
            if attr_name.find('.') != -1:
                relation = attr_name.split('.')[0]
                attr_name = attr_name.split('.')[-1]
            self.order_cond_lst.append(OrderCondition(attr_name, op, relation))

    def _parse_group_by(self):
        self._trim_blank()
        while not self._eof() and not self._test_keyword():
            attr_name, pass_comma = self._read_until_ws_or(',')
            if not pass_comma:
                self._expect_str_wild(',')
            relation = ''
            if attr_name.find('.') != -1:
                relation = attr_name.split('.')[0]
                attr_name = attr_name.split('.')[-1]
            self.aggr_attr_lst.append(AggregationAttr(attr_name, relation))

    def scan(self):
        try:
            while not self._eof():
                kw = self._expect_keyword()
                if kw is None:
                    break
                elif kw == SELECT:
                    self._parse_select()
                elif kw == FROM:
                    self._parse_relations()
                elif kw == WHERE:
                    self._parse_where()
                elif kw == GROUP_BY:
                    self._parse_group_by()
                elif kw == ORDER_BY:
                    self._parse_order_by()
                else:
                    self._read_util_line_break()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            print(str(e))

    def compare(self, new_qep, old_qep, old_sql):
        def _set_ops(new, old):
            added = new - old
            deleted = old - new
            common = new & old
            return common, added, deleted
        def _print(common, added, deleted, decor=''):
            added_texts = ', '.join(list(added))
            deleted_texts = ', '.join(list(deleted))
            common_texts = ', '.join(list(common))
            print('{}common: {}'.format(decor, common_texts))
            print('{}added: {}'.format(decor, added_texts))
            print('{}deleted: {}'.format(decor, deleted_texts))    
        def _match_cond(cond1, cond2):
            # check if two join conds are same
            cond1 = re.sub('[)(]', '', cond1)
            cond2 = re.sub('[)(]', '', cond2)
            cond1_tables = set(re.findall(r'(\w+)\.', cond1))
            cond2_tables = set(re.findall(r'(\w+)\.', cond2))
            cond1_fields = set(re.findall(r'\.(\w+)', cond1))
            cond2_fields = set(re.findall(r'\.(\w+)', cond2))
            if cond1_tables == cond2_tables and cond1_fields == cond2_fields:
                return True
            else:
                return False
        def _unit_id_gen():
            _id = 0
            while True:
                yield str(_id)
                _id += 1
        new_color, old_color = 'green', 'purple'
        new_sql = self
        # check SELECT diff in sql 
        old_select_attrs = set([e.attr for e in old_sql.projections_lst])
        new_select_attrs = set([e.attr for e in new_sql.projections_lst])
        common_select, added_select, deleted_select = _set_ops(new_select_attrs, old_select_attrs)
        #_print(common_select, added_select, deleted_select, 'SELECT ')
        
        ## check WHERE diff in sql
        old_where_strs = set([e.reconstruct_str() for e in old_sql.conditions_lst])
        new_where_strs = set([e.reconstruct_str() for e in new_sql.conditions_lst])
        common_cond, added_cond, deleted_cond = _set_ops(new_where_strs, old_where_strs)
        _print(common_cond, added_cond, deleted_cond, 'WHERE ')
        
        ## Match WHERE cond diff in qep
        # matched_add/del: {sql_str : qep_id}
        wmatched_add, wmatched_del = {}, {}
        for ac in added_cond:
            ac_id = new_qep.search_cond(ac)
            if ac_id > 0:
                wmatched_add[ac] = ac_id
        for dc in deleted_cond:
            dc_id = old_qep.search_cond(dc) 
            if dc_id > 0:
                wmatched_del[dc] = dc_id
        unmatched_old_sql_cond = ', '.join([_str for _str in old_where_strs if _str not in wmatched_del.keys()])
        unmatched_new_sql_cond = ', '.join([_str for _str in new_where_strs if _str not in wmatched_add.keys()])
        
        ## Match SELECT cond diff in qep
        # matched_add/del: {sql_str : qep_id}
        smatched_add, smatched_del = {}, {}
        for ac in added_select:
            ac_ids = new_qep.search_output_id(ac)
            if len(ac_ids) > 0:
                smatched_add[ac] = ac_ids
        for dc in deleted_select:
            dc_ids = old_qep.search_output_id(dc)
            if len(dc_ids) > 0:
                smatched_del[dc] = dc_ids
        unmatched_old_sql_sel = ', '.join([_str for _str in old_select_attrs if _str not in smatched_del.keys()])
        unmatched_new_sql_sel = ', '.join([_str for _str in new_select_attrs if _str not in smatched_add.keys()])
        
        ## Match JOIN type change in two qep trees
        old_join_nodes = old_qep.search_join_nodes()
        new_join_nodes = new_qep.search_join_nodes()
        changed_joins = []
        for ojn in old_join_nodes:
            for njn in new_join_nodes:
                if _match_cond(ojn[0], njn[0]):
                    if ojn[2] != njn[2]: # type changed for same join cond
                        changed_joins += [{'old_id':ojn[1], 'old_type':ojn[2], 'new_id':njn[1], 'new_type':njn[2]}]

        ## Match SCAN type change for same table
        old_scan_nodes = old_qep.search_scan_nodes()
        new_scan_nodes = new_qep.search_scan_nodes()
        changed_scans = []
        for osn in old_scan_nodes:
            for nsn in new_scan_nodes:
                if osn[0] == nsn[0]:
                    if osn[2] != nsn[2]: # type changed for same table scan
                        changed_scans += [{'old_id':osn[1], 'old_type':osn[2], 'new_id':nsn[1], 'new_type':nsn[2]}]

        ## construct visualization
        new_units, old_units = [], []
        new_qep_col, old_qep_col = {}, {}
        new_id, old_id = _unit_id_gen(), _unit_id_gen()
        # SELECT
        new_units.append(DisplayUnit("Nsqlu-"+next(new_id), "SELECT", False))
        old_units.append(DisplayUnit("Osqlu-"+next(old_id), "SELECT", False))
        # sql select fields, qep color
        if self.distinct:
            new_units.append(DisplayUnit("Nsqlu-" + next(new_id), "DISTINCT", False))
            old_units.append(DisplayUnit("Osqlu-" + next(old_id), "DISTINCT", False))

        if len(added_select) > 0:
            new_units.append(DisplayUnit("Nsqlu-"+next(new_id), ", ".join(added_select), True, 
                                        [vi for v in smatched_add.values() for vi in v], new_color))
        for qep_id in [vi for v in smatched_add.values() for vi in v]:
            new_qep_col[qep_id] = new_color

        if len(deleted_select) > 0:
            old_units.append(DisplayUnit("Osqlu-"+next(old_id), ", ".join(deleted_select), True, 
                                        [vi for v in smatched_del.values() for vi in v], old_color))
        for qep_id in [vi for v in smatched_del.values() for vi in v]:
            old_qep_col[qep_id] = old_color
        if len(common_select) > 0:
            new_units.append(DisplayUnit("Nsqlu-"+next(new_id), ", ".join(common_select), False))
            old_units.append(DisplayUnit("Osqlu-"+next(old_id), ", ".join(common_select), False))
        # FROM
        new_units.append(DisplayUnit("Nsqlu-"+next(new_id), "FROM", False))
        old_units.append(DisplayUnit("Osqlu-"+next(old_id), "FROM", False))

        # join on
        for e in new_sql.relations_lst:
            reconstruct_relations_compare(new_id, new_units, e, new_qep)
        for e in old_sql.relations_lst:
            reconstruct_relations_compare(old_id, old_units, e, old_qep)

        # where sql, qep color
        new_units.append(DisplayUnit("Nsqlu-" + str(new_id), "WHERE", False))
        old_units.append(DisplayUnit("Osqlu-" + str(old_id), "WHERE", False))
        if len(added_cond) > 0:
            new_units.append(DisplayUnit("Nsqlu-"+str(new_id), ','.join(added_cond), True, list(wmatched_add.values()), new_color))
        if len(deleted_cond) > 0:
            old_units.append(DisplayUnit("Osqlu-"+str(old_id), ','.join(deleted_cond), True, list(wmatched_del.values()), old_color))
        if len(common_cond) > 0:
            new_units.append(DisplayUnit("Nsqlu-"+str(new_id), ','.join(common_cond), False))
            old_units.append(DisplayUnit("Osqlu-"+str(old_id), ','.join(common_cond), False))
        for v in wmatched_add.values():
            new_qep_col[v] = new_color
        for v in wmatched_del.values():
            old_qep_col[v] = old_color
        # order and aggregation for new_units
        if self.order_cond_lst:
            new_units.append(DisplayUnit("Nsqlu-" + next(new_id), "ORDER BY", False))
            for e in self.order_cond_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                if e.desc:
                    cur_text += " DESC"
                else:
                    cur_text += " ASC"
                new_units.append(DisplayUnit("Nsqlu-"+next(new_id), cur_text, False))
        if self.aggr_attr_lst:
            new_units.append(DisplayUnit("Nsqlu-" + next(new_id), "GROUP BY", False))
            for e in self.aggr_attr_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                new_units.append(DisplayUnit("Nsqlu-"+next(new_id), cur_text, False))
        # order and aggregation for old_units
        if self.order_cond_lst:
            old_units.append(DisplayUnit("Osqlu-" + next(old_id), "ORDER BY", False))
            for e in self.order_cond_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                if e.desc:
                    cur_text += " DESC"
                else:
                    cur_text += " ASC"
                old_units.append(DisplayUnit("Nsqlu-"+next(old_id), cur_text, False))
        if self.aggr_attr_lst:
            old_units.append(DisplayUnit("Osqlu-" + next(old_id), "GROUP BY", False))
            for e in self.aggr_attr_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                old_units.append(DisplayUnit("Osqlu-"+next(old_id), cur_text, False))

        # qep join type change color
        for item in (changed_joins + changed_scans):
            new_qep_col[item['new_id']] = new_color
            old_qep_col[item['old_id']] = old_color

        # qep new/deleted node type 
        new_types = new_qep.search_types()
        old_types = old_qep.search_types()
        added_types = set([n[1] for n in new_types]) - set([n[1] for n in old_types])
        deleted_types = set([n[1] for n in old_types]) - set([n[1] for n in new_types])
        new_col_ = new_qep.assign_color_types(added_types, new_color)
        new_qep_col.update(new_col_)
        old_col_ = old_qep.assign_color_types(deleted_types, old_color)
        old_qep_col.update(old_col_)    
        return old_units, old_qep_col, new_units, new_qep_col


    def reconstruct(self, qep_root):
        units = []
        unit_id = 0
        units.append(DisplayUnit("sqlu-"+str(unit_id), "SELECT", False))
        unit_id += 1
        if self.distinct:
            units.append(DisplayUnit("sqlu-" + str(unit_id), "DISTINCT", True, qep_root.search_unique_id()))
            unit_id += 1
        #pdb.set_trace()
        projection_texts = []
        matches = {}
        for e in self.projections_lst:
            cur_text = e.attr
            if e.name_as:
                cur_text += " AS " + e.name_as
            if e.relation:
                cur_text = e.relation + '.' + cur_text
            output_ids = qep_root.search_output_id(e.attr)
            if len(output_ids) > 0: # there is a match
                output_id = output_ids[0] # choose the first match
                if output_id in matches: # there is already a match on it
                    matches[output_id].append(cur_text)
                else:
                    matches[output_id] = [cur_text]
            else:
                projection_texts.append(cur_text)
        for qep_id, texts in matches.items():
            units.append(DisplayUnit("sqlu-"+str(unit_id), ", ".join(texts), True, qep_id))
            unit_id += 1
        if len(projection_texts) > 0: # have some not matched texts
            units.append(DisplayUnit("sqlu-"+str(unit_id), ", ".join(projection_texts), False))
            unit_id += 1
            #units.append(DisplayUnit("sqlu-"+str(unit_id), ", ".join(projection_texts), False))    
        '''    
        for e in self.projections_lst:
            cur_text = e.attr
            if e.name_as:
                cur_text += " AS " + e.name_as
            if e.relation:
                cur_text = e.relation + '.' + cur_text
            projection_texts.append(cur_text)
        units.append(DisplayUnit("sqlu-"+str(unit_id), ", ".join(projection_texts), False))
        unit_id += 1
        '''
        units.append(DisplayUnit("sqlu-"+str(unit_id), "FROM", False))
        unit_id += 1
        for e in self.relations_lst:
            unit_id = reconstruct_relations(unit_id, units, e, qep_root)
        if self.conditions_lst:
            units.append(DisplayUnit("sqlu-" + str(unit_id), "WHERE", False))
            unit_id += 1
            for e in self.conditions_lst:
                cur_text = ""
                if e.relation:
                    cur_text = e.relation + '.'
                cur_text += e.left + " " + e.op + " " + e.right
                units.append(DisplayUnit("sqlu-"+str(unit_id), cur_text, True, search_cond(qep_root, e)))
                unit_id += 1
        if self.order_cond_lst:
            units.append(DisplayUnit("sqlu-" + str(unit_id), "ORDER BY", False))
            unit_id += 1
            for e in self.order_cond_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                if e.desc:
                    cur_text += " DESC"
                else:
                    cur_text += " ASC"
                qep_match = search_order(qep_root, e, False)
                if qep_match == -1:
                    qep_match = search_order(qep_root, e, False, True)
                units.append(DisplayUnit("sqlu-"+str(unit_id), cur_text, True, qep_match))
                unit_id += 1
        if self.aggr_attr_lst:
            units.append(DisplayUnit("sqlu-" + str(unit_id), "GROUP BY", False))
            unit_id += 1
            for e in self.aggr_attr_lst:
                if e.relation:
                    cur_text = e.relation + "." + e.attr
                else:
                    cur_text = e.attr
                units.append(DisplayUnit("sqlu-"+str(unit_id), cur_text, True, search_group_by(qep_root, e)))
                unit_id += 1

        sql_to_qep = {}
        qep_to_sql = {}
        qep_to_col = {}
        sql_to_col = {}
        color_count = 0
        for u in units:
            if u.qep_id == -1:
                u.matchable = False
            if u.matchable:
                sql_to_qep[u.id] = u.qep_id
                if u.qep_id in qep_to_col.keys():
                    sql_to_col[u.id] = qep_to_col[u.qep_id]
                    u.color = qep_to_col[u.qep_id]
                    continue
                sql_to_col[u.id] = colors[color_count]
                u.color = colors[color_count]
                if u.qep_id not in qep_to_sql.keys():
                    qep_to_sql[u.qep_id] = u.id
                    qep_to_col[u.qep_id] = colors[color_count]
                color_count += 1
        for u in units:
            print(str(u))
        tmp = {}
        for i in range(len(colors)):
            tmp[colors[i]] = color_names[i]
        for k in qep_to_col.keys():
            c = qep_to_col.get(k)
            qep_to_col[k] = tmp.get(c)
        return units, sql_to_qep, qep_to_sql, qep_to_col


if __name__ == '__main__':
    p = SQLParser("SELECT DISTINCT ta.bar as bar "
                  "FROM ta JOIN tb ON ta.id=tb.id JOIN tc ON tc.pd=tb.pd, tf, td Join te ON td.f = te.f "
                  "WHERE ta.id = 5 OR ta.id>13 AND tc.id <= 144 "
                  "ORDER BY ta.id,tb.pd DESC,tc.pd ASC, ta.id DESC , te.f "
                  "GROUP BY tb.pd,ta.id , te.f")
    # p = SQLParser("select a from b where c = d")
    # p = SQLParser("""
    #     SELECT c.state, cat.categoryname,
    #     FROM c
    #         JOIN  ch ON c.customerid = ch.customerid
    #         JOIN  o ON ch.orderid = o.orderid
    #         JOIN  ol ON ol.orderid = o.orderid
    #         JOIN  p ON ol.prod_id = p.prod_id
    #         JOIN  cat ON p.category = cat.category
    #     GROUP BY c.state, cat.categoryname
    #     ORDER BY c.state, o.totalamount DESC""")
    p.scan()

    print("Select Distinct:" + str(p.distinct))
    print("--------")
    print("Projections:")
    for e in p.projections_lst:
        print(str(e))
    print("--------")
    print("Relations:")
    for e in p.relations_lst:
        print(str(e))
    print("--------")
    print("Where Expressions:")
    for e in p.conditions_lst:
        print(str(e))
    print("--------")
    print("Order By:")
    for e in p.order_cond_lst:
        print(str(e))
    print("--------")
    print("Group By:")
    for e in p.aggr_attr_lst:
        print(str(e))

    # print("--------")
    # print("Reconstruct")
    # p.reconstruct(None)

