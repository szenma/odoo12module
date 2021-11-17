odoo.define('fix_account_reports_template.account_report_fix', function (require) {
'use strict';

var AccountReports = require('account_reports.account_report');


 AccountReports.include({

    fold: function(line) {
        var self = this;
        var line_id = line.data('id');
        line.find('.fa-caret-down').toggleClass('fa-caret-right fa-caret-down');
        line.toggleClass('folded');
        $(line).parent('tr').removeClass('o_js_account_report_parent_row_unfolded');
        var $lines_to_hide = this.$el.find('tr[data-parent-id="'+line_id+'"]');
        var index = self.report_options.unfolded_lines.indexOf(line_id);
        if (index > -1) {
            self.report_options.unfolded_lines.splice(index, 1);
        }
        if ($lines_to_hide.length > 0) {
            line.data('unfolded', 'False');
            $lines_to_hide.find('.js_account_report_line_footnote').addClass('folded');
            $lines_to_hide.hide();
            _.each($lines_to_hide, function(el){
                var child = $(el).find('[data-id]:first') && $(el).find('data-parent-id');
                if (child) {
                    self.fold(child);
                }
            })
        }
        return false;
    },
});

});
